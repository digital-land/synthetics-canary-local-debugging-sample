"""
Note: Some parts of the code in this file is translated to Python language from third-party NodeJS package https://github.com/sitespeedio/chrome-har/tree/main
Their license is included in the attribution doc. This was reviewed and approved by Amazon Open Source team.
"""

import json
import asyncio
import logging
import uuid
from datetime import datetime
from .entry_from_response import populate_entry_from_response, finalize_entry
from .cookies import parse_request_cookies, parse_response_cookies
from .headers import get_header_value, parse_header
from .html_utils import get_html_template
from urllib.parse import urlparse, parse_qs, urlunparse
from ..constants import LIBRARY_VERSION
import re

logger = logging.getLogger(__name__)

PAGE_EVENTS = [
    "Page.loadEventFired",
    "Page.domContentEventFired",
    "Page.frameStartedLoading",
    "Page.frameAttached",
    "Page.frameScheduledNavigation"
]

NETWORK_EVENTS = [
    "Network.requestWillBeSent",
    "Network.requestServedFromCache",
    "Network.dataReceived",
    "Network.responseReceived",
    "Network.resourceChangedPriority",
    "Network.loadingFinished",
    "Network.loadingFailed"
]


def find_object(array, property, value):
    return next((x for x in array if x[property] == value), None)


def parse_post_data(content_type, post_data):
    if content_type is None or post_data is None:
        return None
    try:
        if re.match(r"^application\/x-www-form-urlencoded", content_type):
            return {
                "mimeType": content_type,
                "params": parse_qs(urlparse("?" + post_data).query)
            }
        if re.match(r"^application\/json", content_type):
            return {
                "mimeType": content_type,
                "params": parse_qs(post_data)
            }
    except:
        logger.info("Unable to parse post data %s of type %s", post_data, content_type)


def add_from_first_request(page, params):
    if page.get("__timestamp") is None:
        page["__wallTime"] = params.get("wallTime")
        page["__timestamp"] = params.get("timestamp")
        page["startedDateTime"] = datetime.fromtimestamp(params['wallTime']).isoformat()
        #  URL is better than blank, and it's what devtools uses.
        page["title"] = params["request"]["url"] if page.get("title") == "" else page["title"]


def remove_internal_props(obj: dict):
    # __ properties are only for internal use,
    # _ properties are custom properties for the HAR
    for key in list(obj):
        if key.startswith("__"):
            del obj[key]

    return obj


class HarParser:
    def __init__(self, page=None, region=None, **kwargs):
        self._client = page
        self._region = region
        self._path = kwargs.get("path", "/tmp")
        self._save_response = kwargs.get("save_response") or False
        self._capture_mimetypes = kwargs.get("capture_mimetypes") or ["text/html", "application/json"]
        self._inprogress = False
        self._har_contents = None
        self._cleanup()

    def _cleanup(self):
        self._network_events = []
        self._page_events = []
        self._response_body_promises = []

    def set_client(self, page):
        self._client = page

    def set_region(self, region):
        self._region = region

    def reset(self):
        self._client = None
        self._path = None
        self._cleanup()

    async def _setup_event_listeners(self):
        self._client = await self._client.target.createCDPSession()
        await self._client.send("Page.enable")
        await self._client.send("Network.enable")

        def _page_event_listener(_event, _params):
            logger.debug("Handling page event: %s params: %s", _event, json.dumps(_params))
            if not self._inprogress:
                return
            self._page_events.append({"method": _event, "params": _params})

        async def _network_event_listener(_event, _params):
            logger.debug("Handling network event: %s params: %s", _event, json.dumps(_params))
            if not self._inprogress:
                return

            self._network_events.append({"method": _event, "params": _params})

            if self._save_response and _event == "Network.responseReceived":
                response = _params.response
                request_id = _params.requestId

                if response.status != 204 and response.headers.location is None and response.mimeType in self._capture_mimetypes:
                    try:
                        response_body = await self._client.send("Network.getResponseBody",
                                                                {"requestId": request_id})
                        encoding = "base64" if response_body.base64Encoded else None
                        _params.response.body = str(bytearray(response_body.body, encoding))
                    except:
                        # Resources (i.e. response bodies) are flushed after page commits
                        # navigation and we are no longer able to retrieve them. In this
                        # case, fail soft so we still add the rest of the response to the
                        # HAR. Possible option would be force wait before navigation...

                        # fail silently
                        pass

                self._response_body_promises.append(response_body)

        # Page event listeners
        @self._client.on("Page.loadEventFired")
        def callback(params):
            _page_event_listener("Page.loadEventFired", params)

        @self._client.on("Page.domContentEventFired")
        def callback(params):
            _page_event_listener("Page.domContentEventFired", params)

        @self._client.on("Page.frameStartedLoading")
        def callback(params):
            _page_event_listener("Page.frameStartedLoading", params)

        @self._client.on("Page.frameAttached")
        def callback(params):
            _page_event_listener("Page.frameAttached", params)

        @self._client.on("Page.frameScheduledNavigation")
        def callback(params):
            _page_event_listener("Page.frameScheduledNavigation", params)

        # Network event navigation
        @self._client.on("Network.requestWillBeSent")
        async def callback(params):
            await _network_event_listener("Network.requestWillBeSent", params)

        @self._client.on("Network.requestServedFromCache")
        async def callback(params):
            await _network_event_listener("Network.requestServedFromCache", params)

        @self._client.on("Network.dataReceived")
        async def callback(params):
            await _network_event_listener("Network.dataReceived", params)

        @self._client.on("Network.responseReceived")
        async def callback(params):
            await _network_event_listener("Network.responseReceived", params)

        @self._client.on("Network.resourceChangedPriority")
        async def callback(params):
            await _network_event_listener("Network.resourceChangedPriority", params)

        @self._client.on("Network.loadingFinished")
        async def callback(params):
            await _network_event_listener("Network.loadingFinished", params)

        @self._client.on("Network.loadingFailed")
        async def callback(params):
            await _network_event_listener("Network.loadingFailed", params)

    async def start_recording(self):
        logger.debug("Starting recording")
        self._inprogress = True
        await self._setup_event_listeners()
        logger.info("Started recording")

    async def stop_recording(self):
        try:
            logger.debug("Stopping recording")
            self._inprogress = False
            await self._client.detach()
            all_events = self._page_events + self._network_events

            if len(all_events) == 0:
                logger.warning("There are no events recorded. Skipping HAR file generation.")
                return

            self._har_contents = self._generate_har(all_events)
            self._cleanup()
            logger.info("Stopped recording")
            if self._path:
                file = open(self._path, "w+")
                file.write(self.get_har_html())
                file.close()
        except Exception:
            logger.exception("Error while generating HAR file")

    def get_har_json(self):
        return json.dumps(self._har_contents)

    def get_har_html(self, har_contents=None):
        if har_contents is not None:
            return get_html_template(json.dumps(har_contents), self._region)
        else:
            return get_html_template(json.dumps(self._har_contents), self._region)

    def _generate_har(self, events):
        logger.debug("Generating HAR from events")
        logger.debug("Events list size: %s", len(events))

        ignored_reqs = set()
        rootframe_mappings = {}
        pages = []
        entries = []
        entries_without_page = []
        responses_without_page = []
        params_without_page = []
        current_page_id = None

        for event in events:
            params = event["params"]
            method = event["method"]

            if not re.match(r"^(Page|Network)\..+", method):
                continue

            if method == "Page.frameStartedLoading" or method == "Page.frameScheduledNavigation" or method == "Page.navigatedWithinDocument":
                logger.debug("method: %s" % method)
                frame_id = params["frameId"]
                rootframe = rootframe_mappings.get(frame_id, frame_id)

                if any(_page.get("__frameId") == rootframe for _page in pages):
                    continue

                current_page_id = str(uuid.uuid4())
                title = method == params.get("url") if method == "Page.navigatedWithinDocument" else ""
                page = {
                    "id": current_page_id,
                    "startedDateTime": '',
                    "title": title,
                    "pageTimings": {},
                    "__frameId": rootframe
                }
                pages.append(page)
                # do we have any unmapped requests, add them
                if len(entries_without_page) > 0:
                    # update page
                    for entry in entries_without_page:
                        entry["pageref"] = page["id"]
                    entries = entries + entries_without_page
                    add_from_first_request(page, params_without_page[0])

                if len(responses_without_page) > 0:
                    for params in responses_without_page:
                        filtered_entries = list(
                            filter(lambda e: e.get("_requestId") == params.get("requestId"), entries))
                        if len(filtered_entries) > 0:
                            entry = filtered_entries[0]
                            populate_entry_from_response(entry, params.get("response"), page)
                        else:
                            logger.debug("Couldn't find matching request for response")

                # done

            # end
            elif method == "Network.requestWillBeSent":
                logger.debug("method: %s" % method)
                request = params["request"]
                request_id = params["requestId"]
                if not (request["url"].startswith("http") or request["url"].startswith("https")):
                    ignored_reqs.add(request_id)
                    continue

                page = pages[-1] if len(pages) > 0 else None
                cookie_header = get_header_value(request["headers"], "Cookie")
                url = urlparse(request["url"] + request.get("urlFragment", ""))
                post_data = parse_post_data(
                    get_header_value(request["headers"], "Content-type"), request.get("postData"))
                req = {
                    "method": request["method"],
                    "url": urlunparse(url),
                    "queryString": parse_qs(url.query),
                    "postData": post_data,
                    "headersSize": -1,
                    "bodySize": len(request.get("postData", "")),
                    "cookies": parse_request_cookies(cookie_header),
                    "headers": parse_header(request["headers"])
                }
                entry = {
                    "cache": {},
                    "startedDateTime": "",
                    "__requestWillBeSentTime": params.get("timestamp"),
                    "__wallTime": params.get("wallTime"),
                    "_requestId": params.get("requestId"),
                    "__frameId": params.get("frameId"),
                    "_initialPriority": request.get("initialPriority"),
                    "_priority": request.get("initialPriority"),
                    "pageref": current_page_id,
                    "request": req,
                    "time": 0,
                    "_initiator_detail": str(params.get("initiator")),
                    "_initiator_type": params.get("initiator", {}).get("type")
                }
                # The object initiator change according to its type
                initiator_type = params.get("initiator", {}).get("type")
                if initiator_type == "parser":
                    entry["_initiator"] = params["initiator"]["url"]
                    entry["_initiator_line"] = params["initiator"].get("lineNumber", 0) + 1  # Because lineNumber is 0 based

                if initiator_type == "script":
                    if len(params.get("initiator", {}).get("stack", {}).get("callFrames", [])) > 0:
                        top_call_frame = params["initiator"]["stack"]["callFrames"][0]
                        entry["_initiator"] = top_call_frame["url"]
                        entry["_initiator_line"] = top_call_frame["lineNumber"] + 1  # Because lineNumber is 0 based
                        entry["_initiator_column"] = top_call_frame[
                                                         "columnNumber"] + 1  # Because columnNumber is 0 based
                        entry["_initiator_function_name"] = top_call_frame["functionName"]
                        entry["_initiator_script_id"] = top_call_frame["scriptId"]

                if params.get("redirectResponse") is not None:
                    prev_entry = find_object(entries, "_requestId", request_id)
                    if prev_entry is not None:
                        prev_entry["_requestId"] += "r"
                        populate_entry_from_response(prev_entry, params["redirectResponse"], page)
                    else:
                        logger.info("Could not find original request for redirect response: %s", request_id)

                if page is None:
                    logger.info("Request will be sent with requestId %s that can't be mapped to any page at the moment",
                                request_id)
                    entries_without_page.append(entry)
                    params_without_page.append(params)
                    continue

                entries.append(entry)
                # this is the first request for this page, so set timestamp of page.
                add_from_first_request(page, params)
                # wallTime is not necessarily monotonic, timestamp is.
                # So calculate startedDateTime from timestamp diffs.
                entry_secs = page["__wallTime"] + (params["timestamp"] - page["__timestamp"])
                entry["startedDateTime"] = datetime.fromtimestamp(entry_secs).isoformat()
            # end

            elif method == "Network.requestServedFromCache":
                logger.debug("method: %s" % method)
                request_id = params["requestId"]
                if len(pages) < 1:
                    # we haven't loaded any pages yet
                    continue

                if request_id in ignored_reqs:
                    continue

                entry = find_object(entries, "_requestId", request_id)
                if entry is None:
                    logger.info("Received requestServedFromCache for requestId %s with no matching request", request_id)
                    continue

                entry["__servedFromCache"] = True
                entry["cache"]["beforeRequest"] = {
                    "lastAccess": "",
                    "eTag": "",
                    "hitCount": 0
                }

            # end

            elif method == "Network.responseReceived":
                logger.debug("method: %s" % method)
                request_id = params["requestId"]
                if len(pages) < 1:
                    # we haven't loaded any pages yet
                    responses_without_page.append(params)
                    continue

                if request_id in ignored_reqs:
                    continue

                entry = find_object(entries, "_requestId", request_id)
                if entry is None:
                    entry = find_object(entries_without_page, "_requestId", request_id)

                if entry is None:
                    logger.info("Received network response for requestId %s with no matching request", request_id)
                    continue

                frame_id = rootframe_mappings.get(params.get("frameId"), params.get("frameId"))
                page = find_object(pages, "__frameId", frame_id) or pages[-1]
                if page is None:
                    logger.info("Received network response for requestId %s that cannot be mapped to any page",
                                request_id)
                    continue

                try:
                    populate_entry_from_response(entry, params["response"], page)
                except:
                    logger.error("Error parsing response: %s", params)
                    raise

            # end

            elif method == "Network.dataReceived":
                logger.debug("method: %s" % method)
                request_id = params["requestId"]
                if len(pages) < 1:
                    # we haven't loaded any pages yet
                    continue

                if request_id in ignored_reqs:
                    continue

                entry = find_object(entries, "_requestId", request_id)
                if entry is None:
                    logger.info("Received network data for requestId %s with no matching request", request_id)
                    continue

                if entry["response"] is not None:
                    entry["response"]["content"]["size"] += params["dataLength"]

            # end

            elif method == "Network.loadingFinished":
                logger.debug("method: %s" % method)
                request_id = params["requestId"]
                if len(pages) < 1:
                    # we haven't loaded any pages yet
                    continue

                if request_id in ignored_reqs:
                    ignored_reqs.remove(request_id)
                    continue

                entry = find_object(entries, "_requestId", request_id)
                if entry is None:
                    logger.info("Network loading finished for requestId %s with no matching request", request_id)
                    continue

                finalize_entry(entry, params)

            # end

            elif method == "Page.loadEventFired":
                logger.debug("method: %s" % method)
                if len(pages) < 1:
                    # we haven't loaded any pages yet
                    continue

                page = pages[-1]
                if params.get("timestamp") is not None and page.get("__timestamp") is not None:
                    page["pageTimings"]["onLoad"] = (params["timestamp"] - page["__timestamp"]) * 1000

            # end

            elif method == "Page.domContentEventFired":
                logger.debug("method: %s" % method)
                if len(pages) < 1:
                    # we haven't loaded any pages yet
                    continue

                page = pages[-1]
                if params.get("timestamp") is not None and page.get("__timestamp") is not None:
                    page["pageTimings"]["onContentLoad"] = (params["timestamp"] - page["__timestamp"]) * 1000

            # end

            elif method == "Page.frameAttached":
                logger.debug("method: %s" % method)
                frame_id = params["frameId"]
                parent_id = params["parentFrameId"]
                rootframe_mappings[frame_id] = parent_id
                grandparent_id = rootframe_mappings.get(parent_id)
                while grandparent_id is not None:
                    rootframe_mappings[frame_id] = grandparent_id
                    grandparent_id = rootframe_mappings.get(grandparent_id)
            # end

            elif method == "Network.loadingFailed":
                logger.debug("method: %s" % method)
                request_id = params.get("requestId")
                if request_id in ignored_reqs:
                    ignored_reqs.remove(request_id)
                    continue

                entry = find_object(entries, "_requestId", request_id)
                if entry is None:
                    logger.info("Network loading failed for requestId %s with no matching request", request_id)
                    continue

                if params["errorText"] == "net::ERR_ABORTED":
                    finalize_entry(entry, params)
                    logger.info("Loading was canceled due to Chrome or a user action for requestId %s", request_id)
                    continue

                # This could be due to incorrect domain name etc. Sad, but unfortunately not something
                # that a HAR file can represent
                logger.info("Failed to load url %s (cancelled: %s)", entry["request"]["url"], params["canceled"])
                entries = list(filter(lambda _entry: _entry.get("requestId") != request_id, entries))

            # end

            elif method == "Network.resourceChangedPriority":
                logger.debug("method: %s" % method)
                request_id = params["requestId"]
                entry = find_object(entries, "_requestId", request_id)

                if entry is None:
                    logger.info("Received resourceChangedPriority for requestId %s with no matching request",
                                request_id)
                    continue

                entry["_priority"] = event["params"]["newPriority"]

            # end
            else:
                logger.debug("method: %s" % method)
                # logger.debug("Ignored method: %s", method)
                # Keep the old functionality and log unknown events
                ignored_reqs.add(method)

        # dropping resources from disk cache
        # entries = list(filter(lambda _entry: _entry["cache"]["beforeRequest"] is None, entries))

        # dropping incomplete request
        entries = list(filter(lambda _entry: _entry.get("response") is not None, entries))

        # delete internal props
        entries = list(map(remove_internal_props, entries))
        pages = list(map(remove_internal_props, pages))

        page_result = []
        for _page in pages:
            has_entry = any(_entry["pageref"] == _page["id"] for _entry in entries)
            if has_entry:
                page_result.append(page)
            else:
                logger.info("Skipping empty page")
        pages = page_result

        pageref_mapping_result = {}
        for _index, _page in enumerate(pages):
            pageref_mapping_result[_page["id"]] = "page_{}".format(_index + 1)
            _page["id"] = pageref_mapping_result[_page["id"]]

        for _entry in entries:
            _entry["pageref"] = pageref_mapping_result.get(_entry["pageref"])

        return {
            "log": {
                "version": "1.2",  # http spec version
                "creator": {
                    "name": "CloudWatch Synthetics",
                    "version": LIBRARY_VERSION  # har parser library version
                },
                "pages": pages,
                "entries": entries
            }
        }
