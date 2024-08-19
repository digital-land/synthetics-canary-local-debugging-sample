import json
from ..common.utils import ComplexEncoder


class SyntheticsLink:
    def __init__(self, url):
        self.linkNum = 0
        self.url = url
        self.text = ""
        self.parent_url = ""
        self.status = {"statusCode": "", "statusText": ""}
        self.failure_reason = None
        self.screenshots = []

    def with_link_num(self, linkNum):
        self.linkNum = linkNum
        return self

    def with_url(self, url):
        self.url = url
        return self

    def with_text(self, text):
        self.text = text
        return self

    def with_parent_url(self, parentUrl):
        self.parent_url = parentUrl
        return self

    def with_status_code(self, statusCode):
        self.status["statusCode"] = statusCode
        return self

    def with_status_text(self, statusText):
        self.status["statusText"] = statusText
        return self

    def with_failure_reason(self, failureReason):
        self.failure_reason = failureReason
        return self

    def with_screenshot_result(self, screenshotResults):
        self.screenshots = screenshotResults
        return self

    def add_screenshot_result(self, screenshotResult):
        if screenshotResult is not None:
            self.screenshots.append(screenshotResult)

    def get_link_num(self):
        return self.linkNum

    def get_url(self):
        return self.url

    def get_text(self):
        return self.text

    def get_parent_url(self):
        return self.parent_url

    def get_status_code(self):
        return self.status["statusCode"]

    def get_status_text(self):
        return self.status["statusText"]

    def get_failure_reason(self):
        return self.failure_reason

    def get_screenshot_result(self):
        return self.screenshots

    def to_dict(self):
        return dict(
            url=self.url,
            text=self.text,
            parentUrl=self.parent_url,
            status=self.status,
            failureReason=self.failure_reason,
            screenshots=self.screenshots
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, cls=ComplexEncoder)
