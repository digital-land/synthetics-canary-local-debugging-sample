from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from ..common import synthetics_logger as logger
from .constants import *


class SyntheticsBrowser(WebDriver):

    def __init__(self, executable_path=DEFAULT_CHROME_DRIVER_PATH, \
                 chrome_options=None, \
                 synthetics_screenshot=None):
        service = Service(executable_path=executable_path)
        logger.info(executable_path)
        super(SyntheticsBrowser, self).__init__(options=chrome_options, service=service)
        self._browser = super(SyntheticsBrowser, self)
        self._screenshot = synthetics_screenshot
        self.set_viewport_size(width=DEFAULT_VIEWPORT_WIDTH, height=DEFAULT_VIEWPORT_HEIGHT)
        logger.info("ChromeDriver version: " + str(self._browser.capabilities['chrome']['chromedriverVersion']))
        logger.info("Browser version: Chromium " + str(self._browser.capabilities['browserVersion']))

    def get(self, url):
        """
            Go to a URL, loads the web page in the current browser session.
        """
        logger.info("Go to url: %s" % url)
        self._browser.get(url=url)
        logger.info("Loaded url: %s Page title: %s " % (url, self._browser.title))

    def save_screenshot(self, filename, suffix=""):
        """
        Saves a screenshot of the current window to a PNG image file. Returns
           False if there is any IOError, else returns True. Use full paths in
           your filename.

        :Args:
         - filename: Name of file or name of step you wish to save your screenshot with. Screenshots will be stored under /tmp directory
         - suffix: Suffix text to your file name.

        :Usage:
            driver.save_screenshot('foo.png', 'page1')
        """
        logger.info("Taking screenshot of page with title: %s filename: %s suffix: %s" % (
        self._browser.title, filename, suffix))
        return self._screenshot.take(browser=self._browser, step_name=filename, suffix=suffix)

    def set_viewport_size(self, width, height):
        """
        Sets viewport of the browser
        :param width: width of the browser viewport
        :param height: height if the browser viewport
        """
        window_size = self._browser.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
        self._browser.set_window_size(*window_size)

    def execute_script(self, script, *args):
        """
        Synchronously Executes JavaScript in the current window/frame.

        :Args:
         - script: The JavaScript to execute.
         - \*args: Any applicable arguments for your JavaScript.
        """
        logger.info("Synchronously Executing JavaScript in the current window/frame.: %s  args %s" % (script, args))
        return self._browser.execute_script(script, *args)

    def execute_async_script(self, script, *args):
        """
        Asynchronously Executes JavaScript in the current window/frame.

        :Args:
         - script: The JavaScript to execute.
         - \*args: Any applicable arguments for your JavaScript.
        """
        logger.info("Asynchronously Executing JavaScript in the current window/frame.: %s  args %s" % (script, args))
        return self._browser.execute_script(script, *args)

    def close(self):
        """
        Closes the current window.

        :Usage:
            driver.close()
        """
        logger.info("Closing the current window")
        if self._browser is not None:
            self._browser.close()
        return

    def quit(self):
        """
        Quit the browser.

        :Usage:
            driver.quit()
        """
        logger.warning("Browser will be closed at the end of canary run")
        return

    def maximize_window(self):
        """
        Maximizes the current window that webdriver is using
        """
        logger.info("Maximizing current window")
        self._browser.maximize_window()

    def fullscreen_window(self):
        """
        Invokes the window manager-specific 'full screen' operation
        """
        logger.info("Invoking full screen")
        self._browser.fullscreen_window()

    def minimize_window(self):
        """
        Invokes the window manager-specific 'minimize' operation
        """
        logger.info("Minimizing current window")
        self._browser.minimize_window()

    # Navigation
    def back(self):
        """
        Goes one step backward in the browser history.

        :Usage:
            driver.back()
        """
        logger.info("Going back one step in browser history")
        self._browser.back()

    def forward(self):
        """
        Goes one step forward in the browser history.

        :Usage:
            driver.forward()
        """
        logger.info("Going forward one step in browser history")
        self._browser.forward()

    def refresh(self):
        """
        Refreshes the current page.

        :Usage:
            driver.refresh()
        """
        logger.info("Refresh current browser window")
        self._browser.refresh()

    # Timeouts
    def implicitly_wait(self, time_to_wait):
        """
        Sets a sticky timeout to implicitly wait for an element to be found,
           or a command to complete. This method only needs to be called one
           time per session. To set the timeout for calls to
           execute_async_script, see set_script_timeout.

        :Args:
         - time_to_wait: Amount of time to wait (in seconds)

        :Usage:
            driver.implicitly_wait(30)
        """
        logger.info("Invoked implicit wait of %s" % time_to_wait)
        self._browser.implicitly_wait(time_to_wait)

    def set_script_timeout(self, time_to_wait):
        """
        Set the amount of time that the script should wait during an
           execute_async_script call before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait (in seconds)

        :Usage:
            driver.set_script_timeout(30)
        """
        logger.info("Invoked script wait timeout of %s" % time_to_wait)
        self._browser.set_script_timeout(time_to_wait)

    def set_page_load_timeout(self, time_to_wait):
        """
        Set the amount of time to wait for a page load to complete
           before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait

        :Usage:
            driver.set_page_load_timeout(30)
        """
        logger.info("Invoked page load timeout of %s" % time_to_wait)
        self._browser.set_page_load_timeout(time_to_wait)

    def get_user_agent(self):
        """

        :return: user agent string from browser
        """
        self._browser.execute_script("return navigator.userAgent")
