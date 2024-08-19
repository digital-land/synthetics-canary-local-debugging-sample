import json
from ..common import synthetics_logger as logger
from ..common.constants import *
from ..core import BaseSynthetics
from .synthetics_screenshot import SyntheticsScreenshot
from .synthetics_uploader import SyntheticsUploader
from .constants import *
import re


class SyntheticsWebDriver(BaseSynthetics):
    """
        Bootstraps Selenium for executing user canary through Synthetics runtime
    """

    def __init__(self):
        super(SyntheticsWebDriver, self).__init__()
        self._temp_artifacts_path = ARTIFACTS_PATH
        self._uploader = SyntheticsUploader(ARTIFACTS_PATH)
        self._screenshot = SyntheticsScreenshot(ARTIFACTS_PATH)
        self._screenshot.set_uploader(self._uploader)

    def get_http_response(self, url):
        """
            Get response code from http request to url
        """
        import urllib.request as httpClient
        request = httpClient.Request(url, headers={'User-Agent': 'Chrome'})
        responseCode = ''
        try:
            with httpClient.urlopen(request) as response:
                responseCode = response.code
        except Exception as ex:
            logger.error(ex)
            responseCode = "error"
        finally:
            return responseCode

    def Chrome(self, chrome_options = None):
        """
            Launch chrome instance, return the webdriver
        """
        self._is_ui_canary = True
        try:
            if self._browser is not None:
                logger.warning("Selenium Browser already exists.  Reusing existing browser.")
                return self._browser
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from .synthetics_browser import SyntheticsBrowser

            logger.info('Launching browser.')
            if chrome_options is None:
                logger.debug("Using default Chrome options")
                chrome_options = Options()

            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-zygote')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'INFO'})
            chrome_options.set_capability('goog:perfLoggingPrefs', {
                'traceCategories': 'browser,devtools.timeline,devtools',
                'enableNetwork': True,
                'enablePage': True
            })
            if self._canary_user_agent_string is not None:
                chrome_options.add_argument('user-agent=' + self._canary_user_agent_string)
            chrome_options.binary_location = DEFAULT_CHROMIUM_PATH
            logger.info("Creating chromium instance")
            logger.info("Chromium executable exists? " + os.path.exists(DEFAULT_CHROMIUM_PATH))
            self._browser = SyntheticsBrowser(chrome_options=chrome_options, synthetics_screenshot=self._screenshot)
            logger.info("Created chromium instance")
            return self._browser
        except Exception as ex:
            self.add_execution_error("Unable to create chromium", ex)
            logger.error(ex)
            raise

    async def close(self):
        """
            Close browser instance
        """
        try:
            if self._browser is not None:
                self._browser.quit()
                logger.info("Browser closed")
        except Exception as ex:
            self.add_execution_error("Unable to close browser", ex)
        finally:
            self._browser = None

    async def before_canary(self):
        """
            Setup before executing canary
        """
        logger.debug("Starting before_canary()")
        logger.debug("Finished before_canary()")

    async def add_user_agent(self, user_agent_str):
        """
            Add user agent string
        """
        if user_agent_str is None:
            logger.warning("user agent parameter cannot be null or empty.")
            return
        if self._browser is not None:
            logger.error("user agent cannot be added once the browser is created")
            return
        logger.info("Adding %s to user agent header sent with each outbound request." % user_agent_str)

        try:
            user_agent = self._canary_user_agent_string
        except Exception:
            logger.exception("Error getting User Agent from browser.")
        new_user_agent = user_agent + " " + user_agent_str

        try:
            self._canary_user_agent_string = new_user_agent
        except Exception:
            logger.exception("Error while trying to set the User Agent to: %s" % new_user_agent)

    def get_url(self):
        """
        Get the url of current web page
        :return: str of the current url
        """
        if self._browser is None:
            logger.error("A browser instance must be created first before visiting a url")
        return self._browser.current_url

    async def take_screenshot(self, step_name, suffix):
        """
        Synthetics API for taking screenshot and add to reports
        :param step_name: current step name
        :param suffix: suffix to filename
        :return:
        logging is embedded in _browser.save_screenshot
        """
        if self._browser is None:
            logger.error("A browser instance must be created first before visiting a url")

        return self._browser.save_screenshot(step_name, suffix)

    async def generate_har_file(self):
        """
            Process recorded page and network events and generate HAR file
        """
        try:
            if self._browser is None:
                logger.info("No active browser instance. HAR generation will be skipped.")
                return

            self._browser.command_executor._commands.update({
                'getAvailableLogTypes': ('GET', '/session/$sessionId/log/types'),
                'getLog': ('POST', '/session/$sessionId/log')})

            logs = self._browser.execute('getLog', {'type': 'performance'})['value']
            events = []
            for log in logs:
                events.append(json.loads(log['message'])['message'])
            har_content = self._har._generate_har(events)
            self._generate_request_result(events)
            file = open(os.path.join(ARTIFACTS_PATH, HAR_FILE_NAME), 'w')
            file.write(self._har.get_har_html(har_content))
        except Exception as ex:
            logger.exception("Unable to generate har file")
            self.add_execution_error("Unable to generate har file", ex)

    def _generate_request_result(self, events):

        for event in events:
            params = event["params"]
            method = event["method"]

            if not re.match(r"^(Page|Network)\..+", method):
                continue
            if method == "Network.responseReceived":
                if params["response"]:
                    status_code = params["response"]["status"]
                    logger.debug("status code: %s", status_code)
                    if status_code is None:
                        self._request_result.increment_failed_requests()
                    elif 300 > status_code >= 200:
                        self._request_result.increment_successful_requests()
                    elif 400 > status_code >= 300:
                        self._request_result.increment_redirected_requests()
                    elif 500 > status_code >= 400:
                        self._request_result.increment_error_requests()
                    elif 600 > status_code >= 500:
                        self._request_result.increment_fault_requests()
                    else:
                        self._request_result.increment_failed_requests()


    async def close_browser(self):
        """
            Close browser instance
        """
        try:
            if self._browser is not None:
                if self._browser._browser is not None:
                    self._browser._browser.quit()
                    self._browser._browser = None
                self._browser = None
                logger.info("Browser closed")
        except Exception as ex:
            self.add_execution_error("Unable to close browser", ex)
        finally:
            self._browser = None
