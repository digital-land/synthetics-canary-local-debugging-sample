import datetime
import boto3
from .synthetics_logger import synthetics_logger as logger
from .constants import *
from ..reports.requests_result import RequestsResult
from .synthetics_configuration import SyntheticsConfiguration

class SyntheticsMetricsEmitter:
    """
        Class for emitting SyntheticsPuppeteer metrics to CloudWatch
    """
    def __init__(self):
        self._namespace = CLOUDWATCH_NAMESPACE
        self._cloudwatch_client = boto3.client(
            "cloudwatch",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self._synthetics_configuration = SyntheticsConfiguration()

    def set_namespace(self, namespace):
         """
            Set namespace for CloudWatch metric
         """
         self._namespace = namespace

    def configure(self, namespace, synthetics_configuration):
        """
            Set namespace for CloudWatch metric and
        """
        self._namespace = namespace
        self._synthetics_configuration = synthetics_configuration

    def _get_canary_step_level_metric_params(self, metric_name, value, unit, date, canary_name, step_name):
        """
            Get metric data for canary step level
        """
        return {
                "MetricName": metric_name,
                "Dimensions": [
                    {
                        "Name": "CanaryName",
                        "Value": canary_name
                    },
                    {
                        "Name": "StepName",
                        "Value": step_name
                    }
                ],
                "Timestamp": date,
                "Unit": unit,
                "Value": value
            }


    def _get_canary_level_metric_params(self, metric_name, value, unit, date, canary_name):
        """
            Get metric data for canary level
        """
        return {
                "MetricName": metric_name,
                "Dimensions": [
                    {
                        "Name": "CanaryName",
                        "Value": canary_name
                    }
                ],
                "Timestamp": date,
                "Unit": unit,
                "Value": value
            }

    def _get_account_level_metric_params(self, metric_name, value, unit, date):
        """
            Get metric data for account level
        """
        return {
                "MetricName": metric_name,
                "Timestamp": date,
                "Unit": unit,
                "Value": value
            }

    def _put_metric(self, metric_data):
        """
            Util method to publish metrics to CloudWatch
        """
        try:
            start = 0
            end = start + PUT_METRIC_LIMIT
            # publish metrics in batches of PUT_METRIC_LIMIT
            while len(metric_data[start:end]) > 0:
                self._cloudwatch_client.put_metric_data(Namespace=self._namespace, MetricData=metric_data[start:end])
                # slide window
                start = start + PUT_METRIC_LIMIT
                end = start + PUT_METRIC_LIMIT

            logger.debug("Successfully published %s metrics" % str(len(metric_data)))
        except:
            logger.exception("Could not publish metrics")

    def publish_result(self, canary_name, result, start_time_utc=datetime.datetime.now(),
                       end_time_utc=datetime.datetime.now(), invocation_time=datetime.datetime.now(), step_name=None, request_result: RequestsResult=None, step_configuration=None):
        """
            Publish metrics to CloudWatch for given canary and step name (optional)
        """
        if canary_name is None:
            raise RuntimeError("Missing CanaryName. Cannot publish metric to CloudWatch.")

        logger.info("Publishing result and duration CloudWatch metrics with timestamp: %s for Canary: %s  Step: %s  Result: %s Start time: %s End time: %s" % (invocation_time, canary_name, step_name, result, start_time_utc, end_time_utc))
        if result == "PASSED":
            metric_name = "SuccessPercent"
            value = 100.0
            unit = "Percent"
        elif result == "FAILED":
            metric_name = "SuccessPercent"
            value = 0.0
            unit = "Percent"
        elif result == "ERROR":
            metric_name = "Error"
            value = 1.0
            unit = "Count"
        elif result == "SKIPPED":
            metric_name = "Skipped"
            value = 1.0
            unit = "Count"
        elif result == "THROTTLED":
            metric_name = "Throttled"
            value = 1.0
            unit = "Count"
        else:
            metric_name = "Unknown"
            value = 1.0
            unit = "Count"

        duration_in_ms = (end_time_utc - start_time_utc).total_seconds() * 1000  # convert to ms
        if duration_in_ms < 0:
            duration_in_ms = 0

        metric_data = []
        if step_name is not None:
            if step_configuration is None or step_configuration.get_step_success_metric():
                step_level_metric_1 = self._get_canary_step_level_metric_params(metric_name, value, unit, invocation_time, canary_name, step_name)
                metric_data = metric_data + [step_level_metric_1]

            if step_configuration is None or step_configuration.get_step_duration_metric():
                step_level_metric_2 = self._get_canary_step_level_metric_params("Duration", duration_in_ms, "Milliseconds", end_time_utc, canary_name, step_name)
                metric_data = metric_data + [step_level_metric_2]
        else:
            canary_level_metric_1 = self._get_canary_level_metric_params(metric_name, value, unit, invocation_time, canary_name)
            canary_level_metric_2 = self._get_canary_level_metric_params("Duration", duration_in_ms, "Milliseconds", invocation_time, canary_name)

            account_level_metric_1 = self._get_account_level_metric_params(metric_name, value, unit, invocation_time)
            account_level_metric_2 = self._get_account_level_metric_params("Duration", duration_in_ms, "Milliseconds", invocation_time)
            metric_data = metric_data + [canary_level_metric_1, canary_level_metric_2, account_level_metric_1, account_level_metric_2]

            if request_result is not None:
                if self._synthetics_configuration is None or self._synthetics_configuration.get_2xx_metric():
                    canary_level_metric_1 = self._get_canary_level_metric_params("2xx", request_result.get_successful_requests(), "Count", invocation_time, canary_name)
                    metric_data = metric_data + [canary_level_metric_1]
                if self._synthetics_configuration is None or self._synthetics_configuration.get_4xx_metric():
                    canary_level_metric_2 = self._get_canary_level_metric_params("4xx", request_result.get_error_requests(), "Count", invocation_time, canary_name)
                    metric_data = metric_data + [canary_level_metric_2]
                if self._synthetics_configuration is None or self._synthetics_configuration.get_5xx_metric():
                    canary_level_metric_3 = self._get_canary_level_metric_params("5xx", request_result.get_fault_requests(), "Count", invocation_time, canary_name)
                    metric_data = metric_data + [canary_level_metric_3]
                if self._synthetics_configuration is None or self._synthetics_configuration.get_failed_requests_metric():
                    canary_level_metric_4 = self._get_canary_level_metric_params("Failed requests", request_result.get_failed_requests(), "Count", invocation_time, canary_name)
                    metric_data = metric_data + [canary_level_metric_4]

                if self._synthetics_configuration is None or self._synthetics_configuration.get_aggregated_2xx_metric():
                    account_level_metric_1 = self._get_account_level_metric_params("2xx", request_result.get_successful_requests(), "Count", invocation_time)
                    metric_data = metric_data + [account_level_metric_1]
                if self._synthetics_configuration is None or self._synthetics_configuration.get_aggregated_4xx_metric():
                    account_level_metric_2 = self._get_account_level_metric_params("4xx", request_result.get_error_requests(), "Count", invocation_time)
                    metric_data = metric_data + [account_level_metric_2]
                if self._synthetics_configuration is None or self._synthetics_configuration.get_aggregated_5xx_metric():
                    account_level_metric_3 = self._get_account_level_metric_params("5xx", request_result.get_fault_requests(), "Count", invocation_time)
                    metric_data = metric_data + [account_level_metric_3]
                if self._synthetics_configuration is None or self._synthetics_configuration.get_aggregated_failed_requests_metric():
                    account_level_metric_4 = self._get_account_level_metric_params("Failed requests", request_result.get_failed_requests(), "Count", invocation_time)
                    metric_data = metric_data + [account_level_metric_4]

            if result == "FAILED":
                metric_name = "Failed"
                value = 1.0
                unit = "Count"

                if self._synthetics_configuration is None or self._synthetics_configuration.get_failed_canary_metric():
                    canary_level_metric_1 = self._get_canary_level_metric_params(metric_name, value, unit, invocation_time, canary_name)
                    metric_data = metric_data + [canary_level_metric_1]

                if self._synthetics_configuration is None or self._synthetics_configuration.get_aggregated_failed_canary_metric():
                    account_level_metric_1 = self._get_account_level_metric_params(metric_name, value, unit, invocation_time)
                    metric_data = metric_data + [account_level_metric_1]

        self._put_metric(metric_data)
