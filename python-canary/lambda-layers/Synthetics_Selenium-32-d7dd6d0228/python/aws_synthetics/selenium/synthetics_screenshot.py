from ..common import synthetics_logger as logger
from ..reports import ScreenshotResult
from ..core import BaseSyntheticsScreenshot
from .constants import *


class SyntheticsScreenshot(BaseSyntheticsScreenshot):
    """
        Class for managing screenshots
    """
    def __init__(self, location=ARTIFACTS_PATH, starting_num=1, zero_fill=2):
        super(SyntheticsScreenshot, self).__init__(location, starting_num, zero_fill)

    def take(self, browser, step_name, suffix=""):
        """
            Selenium method: Take screenshot for given step and suffix string
        """
        try:
            number_prefix = self.zero_fill(self._count, self._zero_fill)
            if not step_name:
                step_name = "screenshot"
            step_suffix_name = step_name.replace(".png", "")

            if suffix:
                step_suffix_name = step_suffix_name + "-" + suffix

            filename = number_prefix + "-" + step_suffix_name + ".png"
            path = self._location + "/" +filename
            browser.save_screenshot(path)
            self._count += 1

            logger.info("Screenshot saved at %s" % path)
            return self.add_screenshot_result(step_name, filename, browser.current_url)
        except Exception:
            logger.error("Screenshot failed for step name: %s" % step_name)
            raise

    def add_screenshot_result(self, step_name, file_name, page_url):
        """
            Adds screenshot result to map  and
            returns fileName and page url of screenshot
        """
        screenshot_result = ScreenshotResult(file_name, page_url)
        if self._screenshots.get(step_name) is not None:
            self._screenshots[step_name].append(screenshot_result)
        else:
            self._screenshots[step_name] = [screenshot_result]

        if self._uploader is not None:
            upload_errors = self._uploader.upload_screenshots([screenshot_result])
            if upload_errors is not None:
                screenshot_result = screenshot_result.with_error(upload_errors.pop())

        self._current_step_screenshots.append(screenshot_result)
        return screenshot_result
