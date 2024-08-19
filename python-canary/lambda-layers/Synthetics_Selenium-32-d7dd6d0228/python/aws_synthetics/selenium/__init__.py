import io
import subprocess
import sys
import tarfile
from .constants import *
from .synthetics_webdriver import SyntheticsWebDriver
from ..common import synthetics_logger


def _decompress_library():
    import brotli
    files_to_decompress = ["chromium.br", "aws.tar.br", "swiftshader.tar.br", "fonts.tar.br"]
    for name in files_to_decompress:
        synthetics_logger.debug("Decompressing: " + name)
        f = open(PYTHON_SRC_DEP_PATH + 'chromium/' + name, 'rb')
        content = f.read()
        f.close()
        decompressed_libs = brotli.decompress(content)
        if name == "chromium.br":
            with open(CHROMIUM_DIR + "chromium", 'wb') as f:
                f.write(decompressed_libs)
                os.chmod(CHROMIUM_DIR + 'chromium', 0o755)  # Octal value for permissions -rwxr-xr-x
        else:
            with tarfile.open(fileobj=io.BytesIO(decompressed_libs)) as tf:
                tf.extractall(path=CHROMIUM_DIR + name.replace(".tar.br", ""))


def _set_env_variables():
    if not os.path.exists(CHROMIUM_DIR):
        os.makedirs(CHROMIUM_DIR)

    CHROMEDRIVER_SO_PATH = PYTHON_SRC_DEP_PATH + 'bin'
    os.environ['PATH'] = ":".join([PYTHON_SRC_DEP_PATH, os.environ['PATH']])
    os.environ['PYTHONPATH'] = ":".join([PYTHON_SRC_DEP_PATH, os.environ['PYTHONPATH']])
    os.environ['LD_LIBRARY_PATH'] = ":".join([CHROMEDRIVER_SO_PATH, AWS_BIN_PATH, SWIFTSHADER_BIN_PATH, os.environ['LD_LIBRARY_PATH']])
    os.environ['FONTCONFIG_PATH'] = CHROMIUM_DIR + 'fonts'
    os.environ['FONTCONFIG_FILE'] = CHROMIUM_DIR + 'fonts/font.conf'

    sys.path.append(PYTHON_SRC_PATH)
    sys.path.append(PYTHON_SRC_DEP_PATH)


# Synthetics instance
synthetics_webdriver = SyntheticsWebDriver()
synthetics_logger.info("Setting up selenium libraries")
_set_env_variables()
_decompress_library()
synthetics_logger.info("PATH: " + os.environ['PATH'])
synthetics_logger.info("PYTHONPATH: " + os.environ['PYTHONPATH'])
synthetics_logger.info("LD_LIBRARY_PATH: " + os.environ['LD_LIBRARY_PATH'])
synthetics_logger.info("FONTCONFIG_PATH: " + os.environ['FONTCONFIG_PATH'])
synthetics_logger.info("/tmp size: " + subprocess.getoutput('du -sh /tmp'))
synthetics_logger.info("Completed setting up selenium libraries")

# Public methods and objects that can be imported into Synthetics canary
__all__ = [
    "synthetics_webdriver"
]
