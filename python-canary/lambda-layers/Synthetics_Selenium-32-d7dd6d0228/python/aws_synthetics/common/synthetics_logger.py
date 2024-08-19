from datetime import datetime
import logging
from .constants import *
from .utils import stringify_exception

ARTIFACTS_PATH = "/tmp"


class SyntheticsLogger:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, path=ARTIFACTS_PATH, log_level=INFO):
        self.logger = logging.getLogger("synthetics")
        self.logger.setLevel(log_level)
        self.path = path

    def _add_log_file_handler(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        #  format: "2020-05-20T22-01-52-820Z-log.txt"
        file_name = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")[:23] + "Z-log.txt"
        log_handler = logging.FileHandler(os.path.join(path, file_name))
        # log format
        log_handler.setFormatter(logging.Formatter(fmt="{asctime} {levelname}: {msg}", style="{", datefmt="%Y-%m-%dT%H:%M:%SZ"))
        # reset handlers
        self.logger.handlers = []
        # add handlers
        self.logger.addHandler(log_handler)

    def set_path(self, path):
        self.path = path

    def reset(self):
        self.logger.setLevel(logging.INFO)
        self._add_log_file_handler(self.path)

    def set_level(self, log_level):
        self.logger.setLevel(log_level)

    def get_level(self):
        return self.logger.level

    # alias for info log
    def log(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, exc_info=True, **kwargs)


synthetics_logger = SyntheticsLogger()
