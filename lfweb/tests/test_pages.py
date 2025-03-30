"""Tests for the pages module."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

from lfweb.pages.index import IndexHandling
from lfweb.pages.page import Page
from lfweb.tigris.s3 import S3Handler


@pytest.fixture
def s3_mock():
    """Mock S3 interactions for testing."""
    with mock_aws():
        # Setup environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["BUCKET_NAME"] = "test-bucket"

        # Create S3 resources
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        yield s3_client


def test_create_page():
    """Test creating a page."""
    # Use a temporary directory to avoid file system pollution
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        page = Page("TestPage.md", "TestPage")
        content = "This is a test page."

        page.create(content)
        with open(Path(temp_dir, "TestPage.md"), encoding="utf-8") as file:
            assert file.read() == content


def test_render_page():
    """Test rendering a page."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        page = Page("TestPage.md", "TestPage")
        page.create(content)
        assert page.render() == '<p class="pb-4 text-normal">This is a test page.</p>'


def test_get_page_from_endpoint(client):
    """Test getting a page from an endpoint."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        page = Page("TestPage.md", "TestPage")
        page.create(content, "/pages/TestPage")
        # Create the index file
        # index_file = Path(os.environ.get("MD_PATH"), "current_pages.yaml")
        # index = IndexHandling(index_file)
        # index.add("TestPage.md", "TestPage", "/pages/TestPage")
        response = client.get("/pages/TestPage")
        test_page = Path(temp_dir, "TestPage.md")
        assert test_page.exists()
    assert response.status_code == 200
    assert content in response.data.decode("utf-8")


def test_s3_client_type():
    """Test that the S3 client is of the correct type."""
    s3 = S3Handler()
    # Check for a boto3 S3 client type - don't call client() in isinstance
    assert s3.s3_client.__class__.__name__ == "S3"
    # Alternative approach: check if it has S3 client methods
    assert hasattr(s3.s3_client, "list_buckets")
    assert hasattr(s3.s3_client, "upload_file")
    assert hasattr(s3.s3_client, "download_file")


@pytest.mark.integration
def test_s3_upload_file():
    """Test uploading a file to S3."""
    bucket = os.environ["BUCKET_NAME"]
    s3 = S3Handler()
    test_file_path = Path("TestPage.md")
    # Create a test file
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("This is a test file.")
    # Upload the test file
    s3.upload_file(str(test_file_path), "TestPage.md", bucket)
    # Check if the file exists in S3
    response = s3.s3_client.list_objects_v2(Bucket=bucket, Prefix="TestPage.md")
    assert response["KeyCount"] == 1
    # Delete the test file in the s3 bucket
    s3.s3_client.delete_object(Bucket=bucket, Key="TestPage.md")


def test_s3_download_file_with_mock():
    """Test downloading a file from S3 using a mocked S3 client."""

    # Create a mock S3 client
    mock_s3_client = MagicMock()

    # Patch boto3.client to return our mock
    with patch("boto3.client", return_value=mock_s3_client):
        s3 = S3Handler()

        # Test downloading a file
        bucket = "test-bucket"
        s3_key = "test_file.md"
        local_path = "downloaded_file.md"

        s3.download_file(s3_key, local_path, bucket)

        # Assert the S3 client's download_file method was called with correct parameters
        mock_s3_client.download_file.assert_called_once_with(
            Bucket=bucket, Key=s3_key, Filename=local_path
        )


def test_endpoint_for_creating_a_page(client, random_id):
    """Test the endpoint for creating a page."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        pagename = random_id
        response = client.post(
            f"/pages/create/{pagename}", data={"content": content, "title": pagename}
        )
    assert response.status_code == 200
    assert response.json["title"] == pagename
    assert response.json["url"] == f"/pages/{pagename}"
    assert response.json["message"] == f"Page {pagename} created successfully"


def test_endpoint_for_creating_a_page_adds_to_index(client, random_id):
    """Test that the page is added to the index after creation."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        pagename = random_id
        response = client.post(
            f"/pages/create/{pagename}", data={"content": content, "title": pagename}
        )
        index_file = Path(temp_dir, "current_pages.yaml")
        index = IndexHandling(index_file)
        index.load_index()
        assert pagename in index.index
        assert index.index[pagename]["md"] == f"{pagename}.md"
