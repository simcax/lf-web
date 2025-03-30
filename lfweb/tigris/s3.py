"""Class to handle integration to Tigris S3 storage."""

import os

import boto3
from botocore.config import Config


class S3Handler:
    """Class to handle integration to Tigris S3 storage."""

    def __init__(self):
        """Initialize the S3Handler with bucket name and region."""
        self.s3_client = self.init_client()

    def upload_file(self, file_path: str, object_name: str, bucket_name: str):
        """Upload a file to the S3 bucket."""
        self.s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=object_name,
        )
        return self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=object_name)

    def download_file(self, object_name: str, file_path: str, bucket_name: str):
        """Download a file from the S3 bucket."""
        self.s3_client.download_file(
            Bucket=bucket_name,
            Key=object_name,
            Filename=file_path,
        )
        return file_path

    def init_client(self):
        """Get the S3 client."""
        # Placeholder for actual client retrieval logic
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            endpoint_url="https://fly.storage.tigris.dev",
            config=Config(s3={"addressing_style": "virtual"}),
            region_name=os.environ["AWS_REGION"],
        )
        return self.s3_client
