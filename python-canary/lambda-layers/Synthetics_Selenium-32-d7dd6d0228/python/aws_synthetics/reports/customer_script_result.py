import json
import os

from ..common.canary_status import CanaryStatus
from ..common.utils import ComplexEncoder
from .broken_link_checker_report import BrokenLinkCheckerReport
from .requests_result import RequestsResult

ARTIFACTS_PATH = "/tmp"


class CustomerScriptResult:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.status = CanaryStatus.NO_RESULT.value
        self.failure_reason = None
        self.metrics_published = False
        self.requests = RequestsResult()
        self.steps = []
        self.reports = []

    def with_start_time(self, startTime):
        self.start_time = startTime
        return self

    def with_end_time(self, endTime):
        self.end_time = endTime
        return self

    def with_canary_status(self, status):
        self.status = status
        return self

    def with_failure_reason(self, failureReason):
        self.failure_reason = failureReason
        return self

    def with_steps_result(self, stepResult):
        self.steps = stepResult
        return self

    def with_metrics_published(self, metricsPublished):
        self.metrics_published = metricsPublished
        return self

    def with_requests_result(self, requestsResult):
        self.requests = requestsResult
        return self

    def add_report(self, report):
        if isinstance(report, BrokenLinkCheckerReport):
            key = "BrokenLinkChecker"
        else:
            raise Exception("Unsupported report type")

        file_name = key + "Report.json"
        try:
            file = open(os.path.join(ARTIFACTS_PATH, file_name), "w")
            file.write(report.toJson())
        except Exception as ex:
            raise Exception("Unable to create " + file_name + str(ex))

        self.reports.append(file_name)

    def add_step(self, stepResult):
        self.steps.append(stepResult)
        return self

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_status(self):
        return self.status

    def get_failure_reason(self):
        return self.failure_reason

    def get_steps_result(self):
        return self.steps

    def get_reports(self):
        return self.reports

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.status = CanaryStatus.NO_RESULT
        self.metrics_published = None
        self.failure_reason = None
        self.steps = []
        self.reports = []
        if self.requests is None:
            self.requests = RequestsResult()
        else:
            self.requests.reset()

    def to_dict(self):
        return dict(
            startTime=self.start_time.isoformat(),
            endTime=self.end_time.isoformat(),
            status=self.status,
            failureReason=self.failure_reason,
            metricsPublished=self.metrics_published,
            requests=self.requests.__dict__ if self.requests is not None else None,
            steps=self.steps,
            reports=self.reports
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, cls=ComplexEncoder)
