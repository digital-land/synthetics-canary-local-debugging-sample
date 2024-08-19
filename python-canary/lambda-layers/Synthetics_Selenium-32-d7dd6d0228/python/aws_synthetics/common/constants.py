import os

# Library version
MAJOR = 2
MINOR = 0
LIBRARY_VERSION = "{}.{}".format(MAJOR, MINOR)
SYNTHETICS_RUNTIME_VERSION = "syn-python-selenium-2.0"

# Constants common for all modules
SSE_KMS = "aws:kms"
S3_PREFIX = "s3://"
SYNTHETICS_REPORT_NAME = "SyntheticsReport"
HAR_FILE_NAME = "results.har.html"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ARN_SERVICE_NAME = "synthetics"
USER_AGENT_SERVICE_NAME_PREFIX = "CloudWatchSynthetics"
USER_AGENT_SERVICE_VERSION_PREFIX = LIBRARY_VERSION
PUT_METRIC_LIMIT = 20  # max allowed by CloudWatch
CLOUDWATCH_NAMESPACE = "CloudWatchSynthetics"

# ######################### FOR UNIT TESTS ###################################
UNIT_TEST_MODE = os.getenv("UNIT_TEST_MODE")
if UNIT_TEST_MODE == "True":
    DELETE_ARTIFACTS = False
else:
    DELETE_ARTIFACTS = True

TEST_CANARY_NAME = os.getenv("TEST_CANARY_NAME")
TEST_S3_BASE_FILE_PATH = os.getenv("TEST_S3_BASE_FILE_PATH")
################################################################################
