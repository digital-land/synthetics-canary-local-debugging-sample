from .synthetics_config_key import SyntheticsConfigurationKey as ConfigKey

class SyntheticsConfiguration:

    def __init__(self):
        self.config = {
            # Screenshot options
            ConfigKey.SCREENSHOT_ON_STEP_START.value: True,
            ConfigKey.SCREENSHOT_ON_STEP_SUCCESS.value: True,
            ConfigKey.SCREENSHOT_ON_STEP_FAILURE.value: True,

            # Canary reporting configuration
            ConfigKey.INCLUDE_REQUEST_HEADERS.value: False,
            ConfigKey.INCLUDE_RESPONSE_HEADERS.value: False,
            ConfigKey.RESTRICTED_HEADERS.value: [],
            ConfigKey.INCLUDE_REQUEST_BODY.value: False,
            ConfigKey.INCLUDE_RESPONSE_BODY.value: False,

            # Canary execution configuration
            ConfigKey.CONTINUE_ON_STEP_FAILURE.value: False,

            # Step metric configuration
            ConfigKey.STEP_SUCCESS_METRIC.value: True,
            ConfigKey.STEP_DURATION_METRIC.value: True,

            # Canary metric configuration
            ConfigKey.FAILED_REQUESTS_METRIC.value: True,
            ConfigKey.STATUS_2XX_METRIC.value: True,
            ConfigKey.STATUS_4XX_METRIC.value: True,
            ConfigKey.STATUS_5XX_METRIC.value: True,
            ConfigKey.FAILED_CANARY_METRIC.value: True,

            # Canary aggregated metrics configuration
            ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value: True,
            ConfigKey.AGGREGATED_2XX_METRIC.value: True,
            ConfigKey.AGGREGATED_4XX_METRIC.value: True,
            ConfigKey.AGGREGATED_5XX_METRIC.value: True,
            ConfigKey.AGGREGATED_FAILED_CANARY_METRIC.value: True
        }

    def reset(self):
        self.__init__()

    def get_config(self, config_name):
        return self.config.get(config_name)

    def set_config(self, config: dict):
        self.config.update(config)

    # Returns a new SyntheticsConfiguration instance when overriding global configuration
    def create_step_configuration(self, config: dict):
        if not config:
            return self

        synthetics_step_configuration = SyntheticsConfiguration()
        synthetics_step_configuration.set_config(dict(self.get_all_configurations(), **config))
        return synthetics_step_configuration

    def with_screenshot_on_step_start(self, value):
        self.config[ConfigKey.SCREENSHOT_ON_STEP_START.value] = value
        return self

    def with_screenshot_on_step_success(self, value):
        self.config[ConfigKey.SCREENSHOT_ON_STEP_SUCCESS.value] = value
        return self

    def with_screenshot_on_step_failure(self, value):
        self.config[ConfigKey.SCREENSHOT_ON_STEP_FAILURE.value] = value
        return self

    def get_screenshot_on_step_start(self):
        return self.config[ConfigKey.SCREENSHOT_ON_STEP_START.value]

    def get_screenshot_on_step_success(self):
        return self.config[ConfigKey.SCREENSHOT_ON_STEP_SUCCESS.value]

    def get_screenshot_on_step_failure(self):
        return self.config[ConfigKey.SCREENSHOT_ON_STEP_FAILURE.value]

    def enable_step_screenshots(self):
        self.config[ConfigKey.SCREENSHOT_ON_STEP_START.value] = True
        self.config[ConfigKey.SCREENSHOT_ON_STEP_SUCCESS.value] = True
        self.config[ConfigKey.SCREENSHOT_ON_STEP_FAILURE.value] = True

    def disable_step_screenshots(self):
        self.config[ConfigKey.SCREENSHOT_ON_STEP_START.value] = False
        self.config[ConfigKey.SCREENSHOT_ON_STEP_SUCCESS.value] = False
        self.config[ConfigKey.SCREENSHOT_ON_STEP_FAILURE.value] = False

    def with_include_request_headers(self, value):
        self.config[ConfigKey.INCLUDE_REQUEST_HEADERS.value] = value
        return self

    def get_include_request_headers(self):
        return self.config[ConfigKey.INCLUDE_REQUEST_HEADERS.value]

    def with_include_response_headers(self, value):
        self.config[ConfigKey.INCLUDE_RESPONSE_HEADERS.value] = value
        return self

    def get_include_response_headers(self):
       return self.config[ConfigKey.INCLUDE_REQUEST_HEADER.value]

    def with_restricted_headers(self, value):
        self.config[ConfigKey.RESTRICTED_HEADERS.value] = value
        return self

    def get_restricted_headers(self):
        return self.config[ConfigKey.RESTRICTED_HEADERS.value]

    def with_include_request_body(self, value):
        self.config[ConfigKey.INCLUDE_REQUEST_BODY.value] = value
        return self

    def get_include_request_body(self):
        return self.config[ConfigKey.INCLUDE_REQUEST_BODY.value]

    def with_include_response_body(self, value):
        self.config[ConfigKey.INCLUDE_RESPONSE_BODY.value] = value
        return self

    def get_include_response_body(self):
        return self.config[ConfigKey.INCLUDE_RESPONSE_BODY.value]

    def enable_reporting_options(self):
        self.config[ConfigKey.INCLUDE_REQUEST_HEADERS.value] = True
        self.config[ConfigKey.INCLUDE_RESPONSE_HEADERS.value] = True
        self.config[ConfigKey.INCLUDE_REQUEST_BODY.value] = True
        self.config[ConfigKey.INCLUDE_RESPONSE_BODY.value] = True

    def disable_reporting_options(self):
        self.config[ConfigKey.INCLUDE_REQUEST_HEADERS.value] = False
        self.config[ConfigKey.INCLUDE_RESPONSE_HEADERS.value] = False
        self.config[ConfigKey.INCLUDE_REQUEST_BODY.value] = False
        self.config[ConfigKey.INCLUDE_RESPONSE_BODY.value] = False

    def with_continue_on_step_failure(self, value):
        self.config[ConfigKey.CONTINUE_ON_STEP_FAILURE.value] = value
        return self

    def get_continue_on_step_failure(self):
        return self.config[ConfigKey.CONTINUE_ON_STEP_FAILURE.value]

    def with_step_success_metric(self, value):
        self.config[ConfigKey.STEP_SUCCESS_METRIC.value] = value
        return self

    def get_step_success_metric(self):
        return self.config[ConfigKey.STEP_SUCCESS_METRIC.value]

    def with_step_duration_metric(self, value):
        self.config[ConfigKey.STEP_DURATION_METRIC.value] = value
        return self

    def get_step_duration_metric(self):
        return self.config[ConfigKey.STEP_DURATION_METRIC.value]

    def enable_step_metrics(self):
        self.config[ConfigKey.STEP_SUCCESS_METRIC.value] = True
        self.config[ConfigKey.STEP_DURATION_METRIC.value] = True

    def disable_step_metrics(self):
        self.config[ConfigKey.STEP_SUCCESS_METRIC.value] = False
        self.config[ConfigKey.STEP_DURATION_METRIC.value] = False

    def with_failed_requests_metric(self, value):
        self.config[ConfigKey.FAILED_REQUESTS_METRIC.value] = value
        return self

    def get_failed_requests_metric(self):
        return self.config[ConfigKey.FAILED_REQUESTS_METRIC.value]

    def with_2xx_metric(self, value):
        self.config[ConfigKey.STATUS_2XX_METRIC.value] = value
        return self

    def get_2xx_metric(self):
        return self.config[ConfigKey.STATUS_2XX_METRIC.value]

    def with_4xx_metric(self, value):
        self.config[ConfigKey.STATUS_4XX_METRIC.value] = value
        return self

    def get_4xx_metric(self):
        return self.config[ConfigKey.STATUS_4XX_METRIC.value]

    def with_5xx_metric(self, value):
        self.config[ConfigKey.STATUS_5XX_METRIC.value] = value
        return self

    def get_5xx_metric(self):
        return self.config[ConfigKey.STATUS_5XX_METRIC.value]

    def with_aggregated_failed_requests_metric(self, value):
        self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value] = value
        return self

    def get_aggregated_failed_requests_metric(self):
        return self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value]

    def with_aggregated_2xx_metric(self, value):
        self.config[ConfigKey.AGGREGATED_2XX_METRIC.value] = value
        return self

    def get_aggregated_2xx_metric(self):
        return self.config[ConfigKey.AGGREGATED_2XX_METRIC.value]

    def with_aggregated_4xx_metric(self, value):
        self.config[ConfigKey.AGGREGATED_4XX_METRIC.value] = value
        return self

    def get_aggregated_4xx_metric(self):
        return self.config[ConfigKey.AGGREGATED_4XX_METRIC.value]

    def with_aggregated_5xx_metric(self, value):
        self.config[ConfigKey.AGGREGATED_5XX_METRIC.value] = value
        return self

    def get_aggregated_5xx_metric(self):
        return self.config[ConfigKey.AGGREGATED_5XX_METRIC.value]

    def enable_request_metrics(self):
        self.config[ConfigKey.FAILED_REQUESTS_METRIC.value] = True
        self.config[ConfigKey.STATUS_2XX_METRIC.value] = True
        self.config[ConfigKey.STATUS_4XX_METRIC.value] = True
        self.config[ConfigKey.STATUS_5XX_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_2XX_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_4XX_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_5XX_METRIC.value] = True

    def disable_request_metrics(self):
        self.config[ConfigKey.FAILED_REQUESTS_METRIC.value] = False
        self.config[ConfigKey.STATUS_2XX_METRIC.value] = False
        self.config[ConfigKey.STATUS_4XX_METRIC.value] = False
        self.config[ConfigKey.STATUS_5XX_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_2XX_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_4XX_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_5XX_METRIC.value] = False

    def enable_aggregated_request_metrics(self):
        self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_2XX_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_4XX_METRIC.value] = True
        self.config[ConfigKey.AGGREGATED_5XX_METRIC.value] = True

    def disable_aggregated_request_metrics(self):
        self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_2XX_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_4XX_METRIC.value] = False
        self.config[ConfigKey.AGGREGATED_5XX_METRIC.value] = False

    def with_failed_canary_metric(self, value):
        self.config[ConfigKey.FAILED_CANARY_METRIC.value] = value
        return self

    def get_failed_canary_metric(self):
        return self.config[ConfigKey.FAILED_CANARY_METRIC.value]

    def with_aggregated_failed_canary_metric(self, value):
        self.config[ConfigKey.AGGREGATED_FAILED_CANARY_METRIC.value] = value
        return self

    def get_aggregated_failed_canary_metric(self):
        return self.config[ConfigKey.AGGREGATED_FAILED_CANARY_METRIC.value]

    def get_all_configurations(self):
        return self.config

    def to_dict(self):
        screenshotConfigurationDict = dict(
            screenshotOnStepStart=self.config[ConfigKey.SCREENSHOT_ON_STEP_START.value],
            screenshotOnStepSuccess=self.config[ConfigKey.SCREENSHOT_ON_STEP_SUCCESS.value],
            screenshotOnStepFailure=self.config[ConfigKey.SCREENSHOT_ON_STEP_FAILURE.value]
        )

        reportingConfigurationDict = dict(
            includeRequestHeaders = self.config[ConfigKey.INCLUDE_REQUEST_HEADERS.value],
            includeResponseHeaders = self.config[ConfigKey.INCLUDE_RESPONSE_HEADERS.value],
            restrictedHeaders = self.config[ConfigKey.RESTRICTED_HEADERS.value],
            includeRequestBody = self.config[ConfigKey.INCLUDE_REQUEST_BODY.value],
            includeResponseBody = self.config[ConfigKey.INCLUDE_RESPONSE_BODY.value]
        )

        executionConfigurationDict = dict(
            continueOnStepFailure = self.config[ConfigKey.CONTINUE_ON_STEP_FAILURE.value]
        )

        stepMetricsConfigurationDict = dict(
            stepSuccessMetric = self.config[ConfigKey.STEP_SUCCESS_METRIC.value],
            stepDurationMetric = self.config[ConfigKey.STEP_DURATION_METRIC.value]
        )

        canaryMetricsConfigurationDict = dict(
            failedRequestsMetric = self.config[ConfigKey.FAILED_REQUESTS_METRIC.value],
            _2xxMetric = self.config[ConfigKey.STATUS_2XX_METRIC.value],
            _4xxMetric = self.config[ConfigKey.STATUS_4XX_METRIC.value],
            _5xxMetric = self.config[ConfigKey.STATUS_5XX_METRIC.value],
            aggregatedFailedRequestsMetric = self.config[ConfigKey.AGGREGATED_FAILED_REQUESTS_METRIC.value],
            aggregated2xxMetric = self.config[ConfigKey.AGGREGATED_2XX_METRIC.value],
            aggregated4xxMetric = self.config[ConfigKey.AGGREGATED_4XX_METRIC.value],
            aggregated5xxMetric = self.config[ConfigKey.AGGREGATED_5XX_METRIC.value],
            failedCanaryMetric = self.config[ConfigKey.FAILED_CANARY_METRIC.value],
            aggregatedFailedCanaryMetric = self.config[ConfigKey.AGGREGATED_FAILED_CANARY_METRIC.value]
        )

        return dict(
            screenshotConfiguration = screenshotConfigurationDict,
            reportingConfiguration = reportingConfigurationDict,
            executionConfiguration = executionConfigurationDict,
            stepMetricsConfiguration = stepMetricsConfigurationDict,
            canaryMetricsConfiguration = canaryMetricsConfigurationDict
        )
