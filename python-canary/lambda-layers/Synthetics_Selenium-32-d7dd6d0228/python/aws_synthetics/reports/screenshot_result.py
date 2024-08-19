import json


class ScreenshotResult:
    def __init__(self, file_name=None, page_url=None):
        self.file_name = file_name
        self.page_url = page_url
        self.error = None

    def with_file_name(self, file_name):
        self.file_name = file_name
        return self

    def with_page_url(self, page_url):
        self.page_url = page_url
        return self

    def with_error(self, error):
        self.error = error
        return self

    def get_file_name(self):
        return self.file_name

    def get_page_url(self):
        return self.page_url

    def get_error(self):
        return self.error

    def to_dict(self):
        return dict(
            fileName=self.file_name,
            pageUrl=self.page_url,
            error=self.error
        )

    def to_json(self):
        return json.dumps(self.to_dict())
