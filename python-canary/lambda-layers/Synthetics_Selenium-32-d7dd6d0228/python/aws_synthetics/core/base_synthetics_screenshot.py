from abc import ABCMeta, abstractmethod
from ..common import synthetics_logger as logger
from ..reports.screenshot_result import ScreenshotResult


class BaseSyntheticsScreenshot(metaclass=ABCMeta):
    """
           Base class for taking screenshots
       """

    def __init__(self, location="/tmp", starting_num=1, zero_fill=2, uploader=None):
        logger.debug("Screenshots location: %s" % location)
        self._location = location
        self.starting_num = starting_num if starting_num >= 0 else 1
        self._count = self.starting_num
        self._screenshots = {}
        self._current_step_screenshots = []
        self._zero_fill = 2
        self._uploader = uploader
        if zero_fill >= 2:
            self._zero_fill = zero_fill

    def set_uploader(self, uploader):
        """
            Set S3 client for uploading screenshots
        """
        self._uploader = uploader

    def zero_fill(self, num, num_len):
        """
            Prefix number with 0s for given digit length
        """
        return str(num).zfill(num_len)

    def reset(self):
        """
            Reset count to starting number
        """
        self._count = self.starting_num
        self._screenshots = {}
        self._current_step_screenshots = []

    def get_screenshot_result(self, step_name):
        """
            Get all screenshots captured during the execution of this step
            If two steps have same name, it will get screenshots for both of them.
        """
        return self._screenshots.get(step_name)

    def get_current_step_screenshots(self):
        """
            Reads screenshot results captured during the execution of current step.
            Also clears current step screenshots list
        """
        screenshot_results = self._current_step_screenshots
        self._current_step_screenshots = []
        return screenshot_results

    ####################################################################################
    # Subclass must implement these methods
    ####################################################################################

    @abstractmethod
    def take(self, client, step_name="screenshot", suffix="") -> ScreenshotResult:
        """
           Take screenshot for given step and suffix string
        """
        pass

    @abstractmethod
    def add_screenshot_result(self, step_name, file_name, page_url) -> ScreenshotResult:
        """
            Adds screenshot result to map and
            returns file_name and page url of screenshot
        """
        pass
