import json
import inspect
import subprocess
from datetime import datetime
from abc import ABCMeta, abstractmethod
from ..common import ExecutionStatus, HarParser, RequestResponseLogHelper, SyntheticsMetricsEmitter, \
    synthetics_logger as logger, synthetics_configuration, CanaryStatus
from ..reports import SyntheticsReport, RequestsResult, CanaryStepResult
from ..common.constants import *
from ..common.utils import stringify_exception


def _cleanup_chromium_files(path="/tmp"):
    """
        Remove residual core.chromium.* files
    """
    for entry in os.scandir(path):
        if entry.is_file() and entry.name.startswith("core.chromium"):
            try:
                os.remove(entry.path)
                logger.debug("Deleted %s" % entry.path)
            except Exception:
                logger.error("Failed to delete %s" % entry.path)
                logger.warning("This may cause lambda to run out of space.")


def _create_canary_arn(aws_partition, region, aws_account_id, canary_name, canary_id):
    """
        Returns canary ARN string
    """
    if canary_id is not None:
        return "arn:" + aws_partition + ":" + ARN_SERVICE_NAME + ":" + region + ":" + aws_account_id + ":canary:" + canary_name + ":" + canary_id
    return "arn:" + aws_partition + ":" + ARN_SERVICE_NAME + ":" + region + ":" + aws_account_id + ":canary:" + canary_name


class BaseSynthetics(metaclass=ABCMeta):
    def __init__(self, verbose_logging: bool = False):
        self._canary_name = TEST_CANARY_NAME
        self._temp_artifacts_path = "/tmp"
        self._canary_arn = None
        self._canary_id = None
        self._canary_runtime_version = None
        self._canary_user_agent_string = None
        self._artifact_location = None
        self._execution_result = ExecutionStatus.NO_RESULT.value
        self._execution_error = None
        self._har = HarParser()
        self._har_region = None
        self._page = None
        self._browser = None
        self._step_count = 1
        self._invocation_time = None
        self._artifact_upload_error = None
        self._request_response_log_helper = RequestResponseLogHelper()
        self._screenshot = None
        self._metrics_emitter = SyntheticsMetricsEmitter()
        self._synthetics_report = SyntheticsReport()
        self._request_result = RequestsResult()
        self._uploader = None
        self._is_ui_canary = False
        self._step_errors = []
        self._stopped_at_step_failure = False
        self._artifact_s3_location = {"bucket": "", "key": ""}
        self._canary_run_start_time = None
        if verbose_logging:
            self.set_log_level(logger.DEBUG)

    def set_temp_artifact_path(self, path="/tmp"):
        """
            Set path for temporary canary artifacts
        """
        self._temp_artifacts_path = path

    def get_canary_name(self):
        """
            Get Canary name
        """
        return self._canary_name

    def get_canary_id(self):
        """
            Get Canary ID
        """
        return self._canary_id

    def get_canary_arn(self):
        """
            Get Canary ARN
        """
        return self._canary_arn

    def get_canary_user_agent_string(self):
        """
            Get Canary user agent string
        """
        return self._canary_user_agent_string

    def get_runtime_version(self):
        """
            Get Canary runtime version
        """
        return self._canary_runtime_version

    def set_request_response_log_helper(self):
        """
            Set request/response log helper util
        """
        return self._request_response_log_helper

    def get_request_response_log_helper(self):
        """
            Get request/response log helper util
        """
        return self._request_response_log_helper

    def get_log_level(self):
        """
            Get logger level
        """
        return logger.level

    def set_log_level(self, log_level):
        """
            Set logger level
        """
        logger.setLevel(log_level)

    def get_step_errors(self):
        """
            Get step errors
        """
        return self._step_errors

    def set_event_and_context(self, event, context):
        """
            Set event and context to Synthetics instance. This method is invoked from S3 Lambda in Data plane
        """
        if event is None:
            self.add_execution_error("Event object is not provided")
            return

        if context is None:
            self.add_execution_error("Context object is not provided")
            return

        # Moved this line from chrome launch function to support non browser canaries like API canary.
        self._execution_result = ExecutionStatus.PASS_RESULT.value

        try:
            logger.info("Event: %s" % json.dumps(event))
            region = "us-west-2"
            aws_account_id = "123456789012"
            aws_partition = "aws"
            if context is not None and context.invoked_function_arn is not None:
                split_function_arn = context.invoked_function_arn.split(":")
                if len(split_function_arn) > 4:
                    region = split_function_arn[3] or "us-west-2"
                    aws_account_id = split_function_arn[4] or "123456789012"
                    aws_partition = split_function_arn[1] or "aws"

            self._invocation_time = datetime.fromtimestamp(
                event.get("invocationTime", datetime.now().timestamp() * 1000) / 1000)
            self._canary_name = event.get("canaryName", "cloudwatch-synthetics")
            self._canary_id = event.get("canaryId")
            self._canary_arn = _create_canary_arn(aws_partition, region, aws_account_id, self._canary_name,
                                                  self._canary_id)
            self._canary_runtime_version = event.get("runtimeVersion", SYNTHETICS_RUNTIME_VERSION)
            self._canary_user_agent_string = USER_AGENT_SERVICE_NAME_PREFIX + "/" + self._canary_arn + ""
            self._har_region = region
            self._har.set_region(self._har_region)
            self._metrics_emitter.configure(CLOUDWATCH_NAMESPACE, synthetics_configuration)

            artifact_s3_location = event.get("artifactS3Location")
            self._artifact_s3_location = {"bucket": artifact_s3_location.get("s3Bucket"), "key": artifact_s3_location.get("s3Key")}

            self._canary_run_start_time = datetime.fromtimestamp(event.get("canaryRunStartTime", datetime.now().timestamp() * 1000) / 1000)

            self._uploader.set_canary_details(self._canary_name, self._artifact_s3_location, self._invocation_time)
            self._screenshot.set_uploader(self._uploader)

            logger.info("Recording configurations:")
            logger.info("canary_name: %s" % self._canary_name)
            logger.info("artifact_s3_location: s3://%s/%s" % (self._artifact_s3_location.get("bucket"), self._artifact_s3_location.get("key")) )
            logger.info("aws_account_id: %s" % aws_account_id)
            logger.info("region: %s" % region)
            logger.info("canary_arn: %s" % self._canary_arn)
            logger.info("memory_limit_in_mb: %s" % context.memory_limit_in_mb)
            logger.info("aws_request_id: %s" % context.aws_request_id)
            logger.info("remaining_time_in_millis: %s" % context.get_remaining_time_in_millis())
            logger.info("temp_artifacts_path: %s" % self._temp_artifacts_path)
            logger.info("canary_run_start_time: %s" % self._canary_run_start_time)
        except Exception as ex:
            self.add_execution_error("Error while setting event and context for SyntheticsPuppeteer", ex)

    def add_execution_error(self, err_msg, exception=None):
        """
            Handle errors during canary execution
        """
        self._execution_result = ExecutionStatus.FAIL_RESULT.value
        execution_error_str = "{} \n Exception: {}".format(err_msg, str(exception))
        logger.error(execution_error_str)
        if self._execution_error is not None:
            self._execution_error = self._execution_error + " Additional execution exception: " + execution_error_str
            return
        self._execution_error = execution_error_str

    async def start_step(self, step_name, step_configuration):
        """
            Take screenshot when step execution begins
        """
        try:
            logger.info("Step starting: %s URL: %s" % (step_name, self.get_url()))
            if step_configuration is not None and step_configuration.get_screenshot_on_step_start():
                await self.take_screenshot(step_name, "starting")
        except Exception as ex:
            self.add_execution_error("Exception encountered executing start_step in step name: " + step_name, ex)

    async def succeed_step(self, step_name, step_configuration):
        """
            Take screenshot when step execution succeeds
        """
        try:
            logger.info("Step succeeded: %s URL: %s" % (step_name, self.get_url()))
            if step_configuration is not None and step_configuration.get_screenshot_on_step_success():
                await self.take_screenshot(step_name, "succeeded")
        except Exception as ex:
            self.add_execution_error("Exception encountered executing succeed_step in step name: " + step_name, ex)

    async def fail_step(self, step_name, err_msg, step_configuration):
        """
            Take screenshot when step execution fails
        """
        try:
            logger.error("Step failed: %s URL: %s Error: %s" % (step_name, self.get_url(), err_msg))
            if step_configuration is not None and step_configuration.get_screenshot_on_step_failure():
                await self.take_screenshot(step_name, "failed")
        except Exception as ex:
            self.add_execution_error("Exception encountered executing fail_step in step name: " + step_name, ex)

    async def execute_step(self, step_name=None, function_to_execute=None, step_config=None):
        """
            Execute user defined function
        """
        canary_step_result = CanaryStepResult()
        self._step_count += 1
        if step_name is None:
            step_name = "Step" + str(self._step_count)

        step_configuration = synthetics_configuration.create_step_configuration(step_config)

        try:
            await self.start_step(step_name, step_configuration)
            start_time = datetime.now()
            if inspect.iscoroutinefunction(function_to_execute):
                return_value = await function_to_execute()
            else:
                return_value = function_to_execute()
            end_time = datetime.now()
            source_url = self.get_url()
            canary_step_result.with_step_num(self._step_count) \
                .with_step_name(step_name) \
                .with_start_time(start_time) \
                .with_end_time(end_time) \
                .with_source_url(source_url) \
                .with_step_status(CanaryStatus.PASSED.value)
            await self.succeed_step(step_name, step_configuration)
            self._publish_step_result(CanaryStatus.PASSED.value, start_time, end_time, canary_step_result, step_name, step_configuration)
            return return_value
        except Exception as ex:
            logger.error("Exception encountered executing execute_step in step name: %s" % step_name)
            end_time = datetime.now()
            source_url = self.get_url()
            step_error = stringify_exception(ex)
            await self.fail_step(step_name, step_error, step_configuration)
            canary_step_result.with_step_num(self._step_count) \
                .with_step_name(step_name) \
                .with_start_time(start_time) \
                .with_end_time(end_time) \
                .with_source_url(source_url) \
                .with_step_status(CanaryStatus.FAILED.value) \
                .with_failure_reason(step_error)
            self._publish_step_result(CanaryStatus.FAILED.value, start_time, end_time, canary_step_result, step_name, step_configuration)

            step_error = step_error + ' for step: ' + step_name
            self._step_errors.append(step_error)
            if not step_configuration.get_continue_on_step_failure():
                self._stopped_at_step_failure = True
                raise

    def _publish_result(self, result, start_time, end_time, step_name=None, step_configuration=None):
        """
            Publish canary execution result metrics to CloudWatch
        """
        try:
            self._metrics_emitter.publish_result(self._canary_name, result, start_time, end_time, self._invocation_time,
                                                 step_name, self._get_requests_result(), step_configuration)
            return True
        except Exception as ex:
            logger.exception("Exception with publish_result")
            self.add_execution_error(
                "Unable to publish CloudWatch latency and result metrics for canary name: " + self._canary_name + " result: " + result + " with start time: " + start_time + " and end time: " + end_time + " and step_name: " + step_name,
                ex)
            return False

    def _publish_step_result(self, result, start_time, end_time, canary_step_result, step_name=None, step_configuration=None):
        """
            Publish canary execution result metrics to CloudWatch
        """
        try:
            screenshot_result = self._screenshot.get_current_step_screenshots()
            metrics_published = self._publish_result(result, start_time, end_time, step_name, step_configuration)
            destination_url = self.get_url()
            canary_step_result.with_metrics_published(metrics_published)\
                .with_screenshot_result(screenshot_result).with_destination_url(destination_url)
            self._synthetics_report.add_step(canary_step_result)
        except Exception as ex:
            logger.exception("Exception with publish_step_result")
            self.add_execution_error(
                "Unable to publish CloudWatch latency and result metrics for canary name: " + self._canary_name + " result: " + result + " with start time: " + start_time + " and end time: " + end_time + " and step_name: " + step_name,
                ex)

    def _create_execution_report(self, canary_status, canary_error, metrics_published, start_time=datetime.now(),
                                 end_time=datetime.now(), reset_time=0, setup_time=0, launch_time=0):
        try:
            canary_result = self._synthetics_report.get_canary_result()
            canary_result = canary_result.with_start_time(start_time) \
                .with_end_time(end_time) \
                .with_canary_status(canary_status) \
                .with_metrics_published(metrics_published) \
                .with_requests_result(self._get_requests_result()) \
                .with_failure_reason(canary_error)

            self._synthetics_report.with_start_time(start_time) \
                .with_end_time(datetime.now()) \
                .with_canary_name(self._canary_name) \
                .with_customer_script_result(canary_result) \
                .with_time_spent_in_reset(reset_time) \
                .with_time_spent_in_launch(launch_time) \
                .with_time_spent_in_setup(setup_time) \
                .with_execution_status(self._execution_result) \
                .with_execution_error(self._execution_error) \
                .with_configuration(self.get_configuration())

            file = open(os.path.join(self._temp_artifacts_path, SYNTHETICS_REPORT_NAME + "-" + canary_status + ".json"),
                        "w")
            file.write(self._synthetics_report.to_json())
            file.close()
        except Exception as ex:
            logger.exception("Error while generating Synthetics execution report")
            self.add_execution_error("Error while generating Synthetics execution report", ex)

    async def upload_artifacts(self, dir_path="/tmp"):
        """
            Upload artifacts generated by canary (log, screenshots and har) to user's S3 bucket
        """
        logger.info("Uploading artifacts to S3 for canary: %s" % self._canary_name)
        try:
            upload_errors = await self._uploader.upload_artifacts(dir_path)
            if upload_errors is not None and len(upload_errors) > 0:
                self._artifact_upload_error = upload_errors[0]
        except Exception as ex:
            self._artifact_upload_error = ex

    async def after_canary(self, canary_result, canary_error=None, start_time=datetime.now(), end_time=datetime.now(),
                           reset_time=0, setup_time=0, launch_time=0):
        """
            Clean up after canary is executed
        """
        logger.debug("Starting after-canary activities")

        canary_error_msg = str(canary_error) if canary_error is not None else None

        start_time = self._canary_run_start_time

        # If canary execution stopped at an error which could not be handled (fatal), add that first.
        # If multiple step errors, add the error for step which failed first.
        if self._step_errors:
            logger.error("%s step%s failed while executing the canary" % (len(self._step_errors), 's' if len(self._step_errors) > 1 else ''))

            # If fatal canary error is also a step error, do not include it again.
            if canary_error_msg:
                canary_error_msg = canary_error_msg if self._stopped_at_step_failure and len(self._step_errors) == 1 else canary_error_msg + ' Additional error: ' + self._step_errors[0]
            else:
                canary_error_msg = self._step_errors[0]

        await self.generate_har_file()

        metrics_published = self._publish_result(canary_result, start_time, end_time)
        self._create_execution_report(canary_result, canary_error_msg, metrics_published, start_time, end_time,
                                      reset_time, setup_time, launch_time)
        await self.upload_artifacts(self._temp_artifacts_path)
        if self._artifact_upload_error is not None:
            self.add_execution_error("Unable to upload artifacts to S3", self._artifact_upload_error)
        self._artifact_location = self._uploader.get_s3_path() if self._uploader.has_uploaded_artifacts() else None
        _cleanup_chromium_files(self._temp_artifacts_path)
        logger.debug("Finished after-canary activities")
        await self.close_browser()
        logger.debug("/tmp size after canary execution: " + subprocess.getoutput('du -sh /tmp'))
        return {
            "state": canary_result,
            "testRunError": canary_error_msg,
            "executionResult": self._execution_result,
            "executionError": self._execution_error if self._execution_error is None else str(self._execution_error),
            "artifactLocation": self._artifact_location,
            "startTime": start_time.timestamp(),    # epoch seconds
            "endTime": end_time.timestamp(),  # epoch seconds
            "resetTime": reset_time,
            "setupTime": setup_time,
            "launchTime": launch_time,
            "customerStepsStartTime": start_time.timestamp(),
            "customerStepsEndTime": end_time.timestamp()
        }

    def add_report(self, report):
        self._synthetics_report.add_report(report)

    def get_screenshot_result(self, step_name):
        """
            Get screenshot for given step
        """
        return self._screenshot.get_screenshot_result(step_name)

    async def reset(self):
        """
            Reset SyntheticsPuppeteer instance fields with default values
        """
        logger.debug("Reset Synthetics")
        await self.close_browser()

        self._screenshot.reset()
        self._har.reset()
        self._synthetics_report.reset()
        self._request_result.reset()
        self._uploader.reset()
        self._execution_result = ExecutionStatus.NO_RESULT.value
        self._execution_error = None
        self._artifact_location = None
        self._canary_arn = None
        self._canary_name = None
        self._canary_id = None
        self._canary_runtime_version = None
        self._canary_user_agent_string = None
        self._har_region = None
        self._step_count = 0
        self._invocation_time = None
        self._artifact_upload_error = None
        self._step_errors = []
        self._stopped_at_step_failure = False
        self._canary_run_start_time = None
        logger.reset()
        logger.set_path(self._temp_artifacts_path)
        synthetics_configuration.reset()

    # Return global synthetics configuration
    def get_configuration(self):
        """
            Returns Synthetics configuration
        """
        return synthetics_configuration

    def _get_requests_result(self):
        if self._is_ui_canary:
            return self._request_result
        else:
            return None

    ####################################################################################
    # Subclass must implement these methods
    ####################################################################################
    @abstractmethod
    def get_url(self):
        """
            Get URL of current page
        """
        pass

    @abstractmethod
    def add_user_agent(self, page, user_agent_str):
        """
            Add user agent string to Page instance
        """
        pass

    @abstractmethod
    def before_canary(self):
        """
            Setup before executing canary
        """
        pass

    @abstractmethod
    def take_screenshot(self, step_name, suffix):
        """
            Take screenshot of the page
        """
        pass

    @abstractmethod
    def generate_har_file(self):
        """
            Process recorded page and network events and generate HAR file
        """
        pass



