import enum


class ExecutionStatus(enum.Enum):
    """
        Enum for execution status
    """
    PASS_RESULT = "SUCCEEDED"
    FAIL_RESULT = "FAILED"
    NO_RESULT = "ERROR"
