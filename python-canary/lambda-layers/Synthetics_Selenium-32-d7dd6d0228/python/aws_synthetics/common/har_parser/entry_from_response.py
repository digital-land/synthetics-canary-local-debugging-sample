from .headers import calculate_req_header_size, calculate_resp_header_size, parse_header, get_header_value
from .cookies import parse_request_cookies, parse_response_cookies
import re
from datetime import datetime


def deep_get(dictionary, keys, default=None):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)


def format_ip_address(ip_address: str):
    if not isinstance(ip_address, str):
        return None
    #  IPv6 addresses are listed as [2a00:1450:400f:80a::2003]
    return re.sub(r"^\[|]$", "", ip_address)


def parse_optional_time(timing, start, end):
    if timing.get(start) is None or timing.get(end) is None:
        return -1

    if timing.get(start) >= 0 and timing.get(end) >= 0:
        return timing.get(end) - timing.get(start)

    return -1


def first_non_negative(values):
    for val in values:
        if val >= 0:
            return val
    return -1


def is_Http1x(http_protocol):
    return http_protocol.lower().startswith("http/1.")


def populate_entry_from_response(entry, response, page):
    response_headers = response["headers"]
    cookie_header = get_header_value(response_headers, "Set-Cookie")
    text = response["body"] if response.get("body") is not None else None
    entry["response"] = {
        "httpVersion": response["protocol"],
        "redirectUrl": "",
        "status": response['status'],
        "statusText": response["statusText"],
        "content": {
            "mimeType": response["mimeType"],
            "size": 0,
            "text": text
        },
        "headersSize": -1,
        "bodySize": -1,
        "cookies": parse_response_cookies(cookie_header),
        "headers": parse_header(response_headers),
        "_transferSize": response["encodedDataLength"]
    }
    entry["request"]["httpVersion"] = response["protocol"]

    if response.get("fromDiskCache") is True:
        if is_Http1x(response["protocol"]):
            # In http2 headers are compressed, so calculating size from headers text wouldn't be correct.
            entry["response"]["headerSize"] = calculate_resp_header_size(response)

        # h2 push might cause resource to be received before parser sees and requests it.
        if not (response.get("timing", {}).get("pushStart") > 0):
            entry["cache"]["beforeRequest"] = {
                "lastAccess": "",
                "eTag": "",
                "hitCount": 0
            }
    else:
        if response.get("requestHeaders") is not None:
            entry["request"]["headers"] = parse_header(response["requestHeaders"])
            cookie_header = get_header_value(response["requestHeaders"], "Cookie")
            entry["request"]["cookies"] = parse_request_cookies(cookie_header)

        if is_Http1x(response["protocol"]):
            if response.get("headersText") is not None:
                entry["response"]["headersSize"] = len(response["headersText"])
            else:
                entry["response"]["headersSize"] = calculate_resp_header_size(response)

            entry["response"]["bodySize"] = response["encodedDataLength"] - entry["response"]["headersSize"]
            if response.get("requestHeadersText") is not None:
                entry["request"]["headersSize"] = len(response["requestHeadersText"])
            else:
                entry["request"]["headersSize"] = calculate_req_header_size(entry["request"])

    entry["connection"] = str(response.get("connectionId", ""))
    entry["serverIPAddress"] = format_ip_address(response.get("remoteIPAddress"))
    timing = response.get("timing")
    if timing is not None:
        blocked = first_non_negative([timing["dnsStart"], timing["connectStart"], timing["sendStart"]])
        dns = parse_optional_time(timing, "dnsStart", "dnsEnd")
        connect = parse_optional_time(timing, "connectStart", "connectEnd")
        send = timing["sendEnd"] - timing["sendStart"]
        wait = timing["receiveHeadersEnd"] - timing["sendEnd"]
        receive = 0
        ssl = parse_optional_time(timing, "sslStart", "sslEnd")
        entry["timings"] = {
            "blocked": blocked,
            "dns": dns,
            "connect": connect,
            "send": send,
            "wait": wait,
            "receive": receive,
            "ssl": ssl
        }
        entry["_requestTime"] = timing["requestTime"]
        entry["__receiveHeadersEnd"] = timing["receiveHeadersEnd"]
        if timing["pushStart"] >= 0:
            # use the same extended field as WebPageTest
            entry["_was_pushed"] = 1

        entry["time"] = max(0, blocked) + max(0, dns) + max(0, connect) + send + wait + receive
        # Some cached responses generate a Network.requestServedFromCache event,
        # but fromDiskCache is still set to false.
        if entry.get("__servedFromCache") is None:
            #  wallTime is not necessarily monotonic, timestamp is. So calculate startedDateTime from timestamp diffs
            entry_secs = page["__wallTime"] + (timing["requestTime"] - page["__timestamp"])
            entry["startedDateTime"] = datetime.fromtimestamp(entry_secs).isoformat()
            queued_millis = (timing["requestTime"] - entry["__requestWillBeSentTime"]) * 1000
            if queued_millis > 0:
                entry["timings"]["_queued"] = queued_millis

        if entry.get("cache", {}).get("beforeRequest") is not None:
            # lastAccess needs to be a valid date
            entry["cache"]["beforeRequest"]["lastAccess"] = entry["startedDateTime"]
    else:
        entry["timings"] = {
            "blocked": -1,
            "dns": -1,
            "connect": -1,
            "send": 0,
            "wait": 0,
            "receive": 0,
            "ssl": -1,
            "comment": "No timings available from Chrome"
        }
        entry["time"] = 0


def finalize_entry(entry, params):
    timings = entry.get("timings", {})
    timings["receive"] = (params["timestamp"] - entry.get("_requestTime", 0)) * 1000 - entry.get("__receiveHeadersEnd", 0)
    entry["time"] = sum([
        max(0, timings.get("blocked", 0)),
        max(0, timings.get("dns", 0)),
        max(0, timings.get("connect", 0)),
        max(0, timings.get("send", 0)),
        max(0, timings.get("wait", 0)),
        max(0, timings.get("receive", 0))
    ])
    # For cached entries, Network.loadingFinished can have an earlier
    # timestamp than Network.dataReceived

    #  encodedDataLength will be -1 sometimes
    if params.get("encodedDataLength") is not None and params["encodedDataLength"] >= 0:
        response = entry.get("response")
        if response is not None:
            response["_transferSize"] = params["encodedDataLength"]
            response["bodySize"] = params["encodedDataLength"]
            if is_Http1x(response["httpVersion"]) and response["headersSize"] > -1:
                response["bodySize"] -= response["headersSize"]

            compression = max(0, (response["content"]["size"] - response["bodySize"]))
            if compression > 0:
                response["content"]["compression"] = compression


