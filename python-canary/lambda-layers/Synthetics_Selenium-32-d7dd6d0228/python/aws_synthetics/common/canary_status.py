import enum


class CanaryStatus(enum.Enum):
    """
        Enum for Canary status
    """
    PASSED = "PASSED"
    FAILED = "FAILED"
    NO_RESULT = "ERROR"
