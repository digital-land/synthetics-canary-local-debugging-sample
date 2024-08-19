import enum

class SyntheticsConfigurationKey(enum.Enum):
    """
        Enum for Synthetics Configuration
    """
    SCREENSHOT_ON_STEP_START =  "screenshot_on_step_start"
    SCREENSHOT_ON_STEP_SUCCESS = "screenshot_on_step_success"
    SCREENSHOT_ON_STEP_FAILURE = "screenshot_on_step_failure"

    INCLUDE_REQUEST_HEADERS = "include_request_headers"
    INCLUDE_RESPONSE_HEADERS = "include_response_headers"
    RESTRICTED_HEADERS = "restricted_headers"
    INCLUDE_REQUEST_BODY = "include_request_body"
    INCLUDE_RESPONSE_BODY = "include_response_body"

    CONTINUE_ON_STEP_FAILURE = "continue_on_step_failure"

    STEP_SUCCESS_METRIC = "step_success_metric"
    STEP_DURATION_METRIC = "step_duration_metric"

    FAILED_REQUESTS_METRIC = "failed_requests_metric"
    STATUS_2XX_METRIC = "2xx_metric"
    STATUS_4XX_METRIC = "4xx_metric"
    STATUS_5XX_METRIC = "5xx_metric"
    FAILED_CANARY_METRIC = "failed_canary_metric"


    AGGREGATED_FAILED_REQUESTS_METRIC = "aggregated_failed_requests_metric"
    AGGREGATED_2XX_METRIC = "aggregated_2xx_metric"
    AGGREGATED_4XX_METRIC = "aggregated_4xx_metric"
    AGGREGATED_5XX_METRIC = "aggregated_5xx_metric"
    AGGREGATED_FAILED_CANARY_METRIC = "aggregated_failed_canary_metric"
