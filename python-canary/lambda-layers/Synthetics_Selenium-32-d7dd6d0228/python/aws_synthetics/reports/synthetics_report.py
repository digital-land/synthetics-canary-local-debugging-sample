import os
import json
from ..common.execution_status import ExecutionStatus
from ..common.utils import ComplexEncoder
from .customer_script_result import CustomerScriptResult

ARTIFACTS_PATH = "/tmp"


class SyntheticsReport:
    def __init__(self):
        self.canary_name = None
        self.start_time = None
        self.end_time = None
        self.time_spent_in_reset_in_ms = None
        self.time_spent_in_launch_in_ms = None
        self.time_spent_in_setup_in_ms = None
        self.execution_status = ExecutionStatus.NO_RESULT.value
        self.execution_error = None
        self.customer_script = CustomerScriptResult()
        self.configuration = {}

    def with_start_time(self, start_time):
        self.start_time = start_time
        return self

    def with_end_time(self, end_time):
        self.end_time = end_time
        return self

    def with_canary_name(self, canary_name):
        self.canary_name = canary_name
        return self

    def with_time_spent_in_reset(self, time_spent_in_reset_in_ms):
        self.time_spent_in_reset_in_ms = time_spent_in_reset_in_ms
        return self

    def with_time_spent_in_launch(self, time_spent_in_launch_in_ms):
        self.time_spent_in_launch_in_ms = time_spent_in_launch_in_ms
        return self

    def with_time_spent_in_setup(self, time_spent_in_setup_in_ms):
        self.time_spent_in_setup_in_ms = time_spent_in_setup_in_ms
        return self

    def with_customer_script_result(self, customer_script_result):
        self.customer_script = customer_script_result
        return self

    def with_execution_status(self, status):
        self.execution_status = status
        return self

    def with_execution_error(self, error):
        self.execution_error = error
        return self

    def with_configuration(self, config):
        self.configuration = config
        return self

    def add_report(self, report):
        self.customer_script.add_report(report)

    def add_step(self, stepResult):
        self.customer_script.add_step(stepResult)

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_canary_name(self):
        return self.canary_name

    def get_time_spent_in_reset(self):
        return self.time_spent_in_reset_in_ms

    def get_time_spent_in_launch(self):
        return self.time_spent_in_launch_in_ms

    def get_time_spent_in_setup(self):
        return self.time_spent_in_setup_in_ms

    def get_canary_result(self):
        return self.customer_script

    def get_reports(self):
        return self.customer_script.get_reports()

    def get_configuration(self):
        return self.configuration

    def reset(self):
        self.canary_name = None
        self.start_time = None
        self.end_time = None
        self.time_spent_in_reset_in_ms = None
        self.time_spent_in_launch_in_ms = None
        self.time_spent_in_setup_in_ms = None
        self.customer_script.reset()
        self.execution_status = ExecutionStatus.NO_RESULT.value
        self.execution_error = None
        self.configuration = {}

    def to_dict(self):
        return dict(
            canaryName=self.canary_name,
            startTime=self.start_time.isoformat(),
            endTime=self.end_time.isoformat(),
            timeSpentInResetInMs=self.time_spent_in_reset_in_ms,
            timeSpentInLaunchInMs=self.time_spent_in_launch_in_ms,
            timeSpentInSetUpInMs=self.time_spent_in_setup_in_ms,
            executionStatus=self.execution_status,
            executionError=self.execution_error,
            customerScript=self.customer_script.to_dict(),
            configuration=self.configuration.to_dict() if self.configuration is not None else None
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, cls=ComplexEncoder)


