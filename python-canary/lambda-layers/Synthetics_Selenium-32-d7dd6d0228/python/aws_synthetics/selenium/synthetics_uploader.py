import os
from ..core import BaseSyntheticsUploader

UNIT_TEST_MODE = os.getenv("UNIT_TEST_MODE")
if UNIT_TEST_MODE == "True":
    DELETE_ARTIFACTS = False
else:
    DELETE_ARTIFACTS = True

class SyntheticsUploader(BaseSyntheticsUploader):
    def __init__(self, artifacts_path="/tmp"):
        super(SyntheticsUploader, self).__init__(artifacts_path)

    async def upload_artifacts(self, dir_path, delete_files=DELETE_ARTIFACTS):
        """
            Upload canary log, screenshots and HAR files to user's S3 bucket
        """
        result = await super(SyntheticsUploader, self).upload_artifacts_async(dir_path, delete_files)
        return result
