import json

from ..common.utils import ComplexEncoder


class CanaryStepResult:
    def __init__(self):
        self.step_num = None
        self.step_name = None
        self.start_time = None
        self.end_time = None
        self.source_url = None
        self.destination_url = None
        self.status = None
        self.failure_reason = None
        self.screenshots = []
        self.metrics_published = False

    def with_step_num(self, stepNum):
        self.step_num = stepNum
        return self

    def with_step_name(self, stepName):
        self.step_name = stepName
        return self

    def with_start_time(self, startTime):
        self.start_time = startTime
        return self

    def with_end_time(self, endTime):
        self.end_time = endTime
        return self

    def with_step_status(self, stepStatus):
        self.status = stepStatus
        return self

    def with_failure_reason(self, failureReason):
        self.failure_reason = failureReason
        return self

    def with_screenshot_result(self, screenshots):
        self.screenshots = screenshots
        return self

    def with_metrics_published(self, metricsPublished):
        self.metrics_published = metricsPublished
        return self

    def with_source_url(self, url):
        self.source_url = url
        return self

    def with_destination_url(self, url):
        self.destination_url = url
        return self

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_status(self):
        return self.status

    def get_failure_reason(self):
        return self.failure_reason

    def get_screenshots(self):
        return self.screenshots

    def get_metrics_published(self):
        return self.metrics_published

    def get_step_num(self):
        return self.step_num

    def get_step_name(self):
        return self.step_name

    def get_source_url(self):
        return self.source_url

    def get_destination_url(self):
        return self.destination_url

    def to_dict(self):
        return dict(
            stepNum=self.step_num,
            stepName=self.step_name,
            startTime=self.start_time.isoformat(),
            endTime=self.end_time.isoformat(),
            sourceUrl=self.source_url,
            destinationUrl=self.destination_url,
            status=self.status,
            failureReason=self.failure_reason,
            screenshots=self.screenshots,
            metricsPublished=self.metrics_published
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, cls=ComplexEncoder)