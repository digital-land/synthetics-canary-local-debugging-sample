import json


class RequestResponseLogHelper:
    """
        Class for converting http request/response to strings for logging
    """

    def __init__(self):
        self._request = {"url": True, "resourceType": False, "method": False, "headers": False, "postData": False}
        self._response = {"status": True, "statusText": True, "url": True, "headers": False}

    def with_log_request_url(self, url):
        self._request["url"] = url
        return self

    def with_log_request_resource_type(self, resource_type):
        self._request["resourceType"] = resource_type
        return self

    def with_log_request_method(self, method):
        self.request["method"] = method
        return self

    def with_log_request_headers(self, headers):
        self._request["headers"] = headers
        return self

    def with_log_request_post_data(self, post_data):
        self._request["postData"] = post_data
        return self

    def with_log_response_status(self, status):
        self._request["status"] = status
        return self

    def with_log_response_status_text(self, status_text):
        self._response["statusText"] = status_text
        return self

    def with_log_response_url(self, url):
        self._response["url"] = url
        return self

    def with_log_response_remote_address(self, remote_address):
        self._response["remoteAddress"] = remote_address
        return self

    def with_log_response_headers(self, headers):
        self._response["headers"] = headers
        return self

    def get_log_request_string(self, request):
        """
            Stringify Request object
        """
        log_request_str = ""
        if request is None:
            return log_request_str

        log_request_str = "url: {} resourceType: {} method: {} header: {}".format(
            request.url,
            request.resourceType,
            request.method,
            json.dumps(request.headers)
        )

        if request.postData is not None:
            log_request_str = "{} postData: {}".format(log_request_str, json.dumps(request.postData))

        return log_request_str

    def get_log_response_string(self, response):
        """
            Stringify Response object
        """
        log_response_str = ""
        if response is None:
            return log_response_str

        # TODO: revisit
        # "statusText" and "remoteAddress" are not available on response object
        return "status: {} url: {} header: {}".format(
            str(response.status),
            response.url,
            json.dumps(response.headers)
        )

