import json


class RequestsResult:
    def __init__(self):
        self.failed = 0
        self._2xx = 0
        self._4xx = 0
        self._5xx = 0
        self._3xx = 0

    def increment_successful_requests(self):
        self._2xx += 1

    def increment_failed_requests(self):
        self.failed += 1

    def increment_error_requests(self):
        self._4xx += 1

    def increment_fault_requests(self):
        self._5xx += 1

    def increment_redirected_requests(self):
        self._3xx += 1

    def get_successful_requests(self):
        return self._2xx

    def get_failed_requests(self):
        return self.failed

    def get_error_requests(self):
        return self._4xx

    def get_fault_requests(self):
        return self._5xx

    def get_redirected_requests(self):
        return self._3xx

    def reset(self):
        self.failed = 0
        self._2xx = 0
        self._4xx = 0
        self._5xx = 0
        self._3xx = 0

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.to_dict())
