# Selenium specific constants
import os
ARTIFACTS_PATH = os.getenv("SELENIUM_HOME", "/tmp")

PYTHON_SRC_PATH = "/opt/python/"
PYTHON_SRC_DEP_PATH = "/opt/python/lib/"
CHROMIUM_DIR = "/tmp/chromium/"
DEFAULT_CHROMIUM_PATH = "/tmp/chromium/chromium"
DEFAULT_CHROME_DRIVER_PATH = "/opt/python/lib/chromedriver"
AWS_BIN_PATH = "/tmp/chromium/aws/"
SWIFTSHADER_BIN_PATH = "/tmp/chromium/swiftshader/"

DEFAULT_VIEWPORT_WIDTH = 1920
DEFAULT_VIEWPORT_HEIGHT = 1080