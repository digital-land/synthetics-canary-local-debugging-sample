import os
import datetime
import json
import sys
import asyncio
from typing import List
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError
from abc import ABCMeta, abstractmethod
from ..common.synthetics_logger import synthetics_logger as logger
from ..reports.screenshot_result import ScreenshotResult
from ..common.constants import *


class BaseSyntheticsUploader(metaclass=ABCMeta):
    def __init__(self, artifacts_path="/tmp"):
        self.canary_name = None
        self.invocation_time = None
        self.s3_upload_location = {"bucket": "", "key": ""}
        self.s3_client = None
        self.setup_error = None
        self.setup_done = False
        # True if at least one artifact has been uploaded to s3 upload location
        self.uploaded_artifacts = False
        self.artifacts_path = artifacts_path

    def set_canary_details(self, canary_name, artifact_s3_location, invocation_time):
        self.canary_name = canary_name
        self.s3_upload_location = artifact_s3_location
        self.invocation_time = invocation_time

    def has_uploaded_artifacts(self):
        return self.uploaded_artifacts

    def get_s3_path(self):
        if not self.s3_upload_location["bucket"]:
            return None
        return os.path.join(self.s3_upload_location["bucket"], self.s3_upload_location["key"])

    def set_s3_client(self):
        self.setup_done = True
        try:
            self.s3_client = self.get_s3_client()
            self._verify_bucket_ownership()
        except Exception as ex:
            self.setup_error = ex
            raise

    def get_s3_client(self):
        if self.s3_client is not None:
            return self.s3_client

        try:
            self.s3_client = boto3.client("s3",
                                aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                aws_session_token=AWS_SESSION_TOKEN,
                                region_name=AWS_REGION)
            s3_bucket = self.s3_upload_location["bucket"]
            current_region = AWS_REGION
            bucket_region = None
            try:
                logger.debug("Getting Bucket location for s3Bucket: %s" % json.dumps(s3_bucket))
                get_bucket_location_output = self.s3_client.get_bucket_location(Bucket=s3_bucket)
                bucket_region = get_bucket_location_output.get("LocationConstraint")
                # Handle special responses
                if bucket_region == '' or bucket_region is None:
                    bucket_region = 'us-east-1'
                elif bucket_region == 'EU':
                    bucket_region = 'eu-west-1'
                logger.info('S3 Bucket location determined: ' + bucket_region)
            except Exception as ex:
                self.bucket_location_error =  "Unable to fetch S3 bucket location: %s" % ex
                logger.error(self.bucket_location_error)
                raise ex

            bucket_region = bucket_region or current_region
            if bucket_region != current_region:
                self.s3_client = boto3.client("s3",
                                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                    aws_session_token=AWS_SESSION_TOKEN,
                                    region_name=bucket_region)
            return self.s3_client
        except Exception as ex:
            logger.exception("Error getting S3 client: %s" % json.dumps(ex))
            raise ex

    def upload_screenshots(self, screenshots: List[ScreenshotResult], delete_files=True):
        """
            Upload screenshots to S3 bucket
        """
        upload_artifact_errors = []
        try:
            files = [os.path.join(self.artifacts_path, screenshot.get_file_name()) for screenshot in screenshots]
            logger.debug("Uploading screenshots: %s" % files)
            num_files_uploaded, file_upload_errors = self._upload_files_to_s3(files)
            if delete_files:
                files_removed, file_remove_errors = self._delete_temp_files(files)
            else:
                files_removed, file_remove_errors = ([], [])
            upload_artifact_errors = file_upload_errors + file_remove_errors
        except Exception as ex:
            upload_artifact_errors.append(ex)
            logger.exception("Error while uploading screenshots")
        finally:
            logger.debug("Uploaded screenshots")
            if len(upload_artifact_errors) > 0:
                logger.error(str(upload_artifact_errors))
                return upload_artifact_errors
            else:
                return None

    def upload_artifacts(self, dir_path, delete_files=True):
        """
            Upload canary log, screenshots and HAR files to user's S3 bucket
        """
        upload_artifact_errors = []
        files = []

        # scan and filter unwanted files from artifacts directory
        try:
            for entry in os.scandir(dir_path):
                if entry.is_file() and not entry.name.startswith(".") and not entry.name.startswith("core.chromium"):
                    files.append(entry.path)
        except Exception as ex:
            logger.exception("Scanning files in %s failed" % dir_path)
            upload_artifact_errors.append(ex)
            return upload_artifact_errors

        # upload files
        try:
            logger.info("Uploading files to S3: %s" % json.dumps(files))
            num_files_uploaded, file_upload_errors = self._upload_files_to_s3(files)
            if num_files_uploaded > 0:
                self.uploaded_artifacts = True  # At least one artifact uploaded.
            if len(file_upload_errors) > 0:
                upload_artifact_errors = file_upload_errors
                logger.error(str(upload_artifact_errors))
        except Exception as ex:
            upload_artifact_errors.append(ex)
            logger.exception("Error while uploading canary artifacts")
        finally:
            # delete temp files
            if delete_files or delete_files is None:
                files_removed, file_remove_errors = self._delete_temp_files(files)
                if len(file_remove_errors) > 0:
                    upload_artifact_errors = upload_artifact_errors + file_remove_errors

            if len(upload_artifact_errors) > 0:
                return upload_artifact_errors
            else:
                return None

    async def upload_artifacts_async(self, dir_path, delete_files=True):
        """
            Upload canary log, screenshots and HAR files to user's S3 bucket
        """
        upload_artifact_errors = []
        files = []

        # scan and filter unwanted files from artifacts directory
        try:
            for entry in os.scandir(dir_path):
                if entry.is_file() and not entry.name.startswith(".") and not entry.name.startswith("core.chromium"):
                    files.append(entry.path)
        except Exception as ex:
            logger.exception("Scanning files in %s failed" % dir_path)
            upload_artifact_errors.append(ex)
            return upload_artifact_errors

        # upload files
        try:
            logger.info("Uploading files to S3: %s" % json.dumps(files))
            num_files_uploaded, file_upload_errors = await self._upload_files_to_s3_async(files)
            if num_files_uploaded > 0:
                self.uploaded_artifacts = True  # At least one artifact uploaded.
            if len(file_upload_errors) > 0:
                upload_artifact_errors = file_upload_errors
                logger.error(str(upload_artifact_errors))
        except Exception as ex:
            upload_artifact_errors.append(ex)
            logger.exception("Error while uploading canary artifacts")
        finally:
            # delete temp files
            if delete_files or delete_files is None:
                files_removed, file_remove_errors = self._delete_temp_files(files)
                if len(file_remove_errors) > 0:
                    upload_artifact_errors = upload_artifact_errors + file_remove_errors

            if len(upload_artifact_errors) > 0:
                return upload_artifact_errors
            else:
                return None

    def reset(self):
        self.canary_name = None
        self.invocation_time = None
        self.s3_upload_location = {"bucket": "", "key": ""}
        self.s3_client = None
        self.setup_error = None
        self.setup_done = False
        self.uploaded_artifacts = False

    def _verify_bucket_ownership(self):
        """
            Verify ownership of the S3 bucket
        """
        bucket = self.s3_upload_location["bucket"]
        logger.debug("Verifying bucket ownership for %s" % bucket)
        found = False
        try:
            response = self.s3_client.list_buckets()
            for bkt in response["Buckets"]:
                if bkt["Name"] == bucket:
                    found = True
                    break
            logger.debug("Verified bucket ownership for %s" % bucket)
        except ClientError:
            logger.exception(
                "Exception calling ListBuckets. Unable to determine the bucket ownership for bucket: %s" % bucket)
            raise
        if not found:
            raise RuntimeError("S3 bucket {} is not owned by this AWS account".format(bucket))

    def _read_temp_dir(self):
        """
            Get list of files in artifacts directory
        """
        logger.info("Getting list of files under /tmp to upload to S3")
        try:
            files = os.listdir(self.artifacts_path)
            logger.info("List of files under %s: %s" % (self.artifacts_path, str(files)))
            return files
        except:
            logger.exception("Error getting list of files from /tmp.")
            raise

    def _upload_file(self, file: str):
        bucket = self.s3_upload_location["bucket"]
        key = self.s3_upload_location["key"]
        try:
            with open(file, "rb") as f:
                file_contents = f.read()
                file_s3_path = os.path.join(bucket, key, os.path.basename(f.name))
                params = {}
                if file.endswith(".html") or file.endswith("txt"):
                    params["ContentType"] = "text/html; charset=UTF-8"

                response = self.s3_client.put_object(
                    Bucket=bucket,
                    Key=os.path.join(key, os.path.basename(f.name)),
                    Body=file_contents,
                    ServerSideEncryption=SSE_KMS,
                    ContentType=params.get("ContentType", "")
                )
                logger.debug("Finished uploading file at %s" % file_s3_path)
                logger.debug(json.dumps(response))
                return {"upload_successful": True}
        except Exception as ex:
            logger.exception("Failed to upload file %s" % file)
            return {"upload_successful": False, "error": ex}

    async def _upload_file_async(self, file):
        return self._upload_file(file)

    def _upload_files_to_s3(self, files: List[str]):
        """
            Util method to upload objects to S3 bucket
        """
        if self.setup_error is not None:
            raise Exception(self.setup_error)

        if not self.setup_done:
            self.set_s3_client()

        file_upload_errors = []
        num_files_uploaded = 0
        results = [self._upload_file(file) for file in files]
        for result in results:
            if isinstance(result, Exception):
                file_upload_errors.append(result)
            else:
                if result.get("upload_successful"):
                    num_files_uploaded += 1
                elif result.get("error") is not None:
                    file_upload_errors.append(result.get("error"))

        return num_files_uploaded, file_upload_errors

    async def _upload_files_to_s3_async(self, files: List[str]):
        """
            Util method to upload objects to S3 bucket
        """
        if self.setup_error is not None:
            raise Exception(self.setup_error)

        if not self.setup_done:
            self.set_s3_client()

        file_upload_errors = []
        num_files_uploaded = 0
        tasks = [self._upload_file_async(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                file_upload_errors.append(result)
            else:
                if result.get("upload_successful"):
                    num_files_uploaded += 1
                elif result.get("error") is not None:
                    file_upload_errors.append(result.get("error"))

        return num_files_uploaded, file_upload_errors

    def _delete_temp_files(self, files: List[str]):
        """
            Delete files in artifacts directory
        """
        logger.info("Removing temp files %s" % json.dumps(files))
        files_removed = []
        file_remove_errors = []
        for file in files:
            try:
                os.remove(file)
                files_removed.append(file)
            except OSError:
                tb = sys.exc_info()[2]
                file_remove_errors.append(traceback.format_tb(tb))
                logger.exception("Error removing file: %s", file)
        return files_removed, file_remove_errors
