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


def test_create_page(temp_dir):
    """Test creating a page."""
    # Use a temporary directory to avoid file system pollution
    os.environ["MD_PATH"] = temp_dir
    content = "This is a test page."
    title = "test page"
    page = Page(title)
    page.create(content)
    with open(Path(temp_dir, "test-page.md"), encoding="utf-8") as file:
        assert file.read() == content
    expected_url = "/pages/test-page"
    assert page.url == expected_url


def test_create_sub_page(temp_dir, index_content_basic_2):
    """Test creating a sub page"""
    # Use a temporary directory to avoid file system pollution
    os.environ["MD_PATH"] = temp_dir
    # Add a sub page to the test page
    title = "This is my test page"
    content = "This is a test page."
    page = Page(title)
    main_page_md = page.create(content)
    # Add the sub page
    sub_title = "This is my sub test page"
    sub_content = "This is a sub test page."
    sub_page = Page(sub_title, main_page_md)
    sub_page.create(sub_content)
    # Check if the sub page was created
    with open(
        Path(temp_dir, "this-is-my-test-page.this-is-my-sub-test-page.md")
    ) as file:
        assert file.read() == sub_content
    expected_url = "/pages/this-is-my-test-page/this-is-my-sub-test-page"
    assert sub_page.url == expected_url


# Tests for retrieving the page content
def test_get_page_content(temp_dir):
    """Test getting the content of a page."""
    # Use a temporary directory to avoid file system pollution
    os.environ["MD_PATH"] = temp_dir
    content = "This is a test page."
    title = "Test page"
    page = Page(title)
    page.create(content)
    md_content = page.md_content()
    assert md_content == content


def test_render_page(temp_dir):
    """Test rendering a page."""
    os.environ["MD_PATH"] = temp_dir
    content = "This is a test page."
    title = "Test page"
    page = Page(title)
    page.create(content)
    assert page.render() == '<p class="pb-4 text-normal">This is a test page.</p>'


def test_render_sub_page(temp_dir):
    """Test creating a sub page"""
    # Use a temporary directory to avoid file system pollution
    os.environ["MD_PATH"] = temp_dir
    # Add a sub page to the test page
    title = "This is my test page"
    content = "This is a test page."
    page = Page(title)
    main_page_md = page.create(content)
    # Add the sub page
    sub_title = "This is my sub test page"
    sub_content = "This is a sub test page."
    sub_page = Page(sub_title, main_page_md)
    sub_page.create(sub_content)
    # Check if the sub page can be rendered
    assert (
        sub_page.render() == '<p class="pb-4 text-normal">This is a sub test page.</p>'
    )


def test_update_page(temp_dir):
    """Tests the update function for the page class"""
    os.environ["MD_PATH"] = temp_dir
    content = "Original content"
    title = "original title"
    page = Page(title)
    # Create the page with the content
    md_filename = page.create(content=content)

    # Now update the content in the page
    new_content = "Some other content"
    result = page.update(content=new_content, original_title=title)
    assert result == md_filename
    with open(Path(md_filename)) as page_file:
        file_content = page_file.read()
    assert file_content == new_content


def test_update_titlepage_title(temp_dir):
    os.environ["MD_PATH"] = temp_dir
    content = "This is a test page."
    original_title = "Original Title"
    page = Page(original_title)
    # Create the page with the content
    page_filepath = page.create(content)
    # Now update the title in the page
    new_title = "Updated Title"
    new_page_path = page.update(
        content=content, original_title=original_title, new_title=new_title
    )
    with open(new_page_path, encoding="utf-8") as file:
        file_content = file.read()
    assert file_content == content
    assert page_filepath.exists() is False
    # Check if the title was updated
    index = IndexHandling()
    index.load_index()
    assert index.index["updated-title"]["title"] == new_title


def test_update_title_on_subpage(temp_dir):
    """Testing a subpage title can be changed"""
    os.environ["MD_PATH"] = temp_dir
    content = "Original content"
    title = "original title"
    page = Page(title)
    # Create the page with the content
    md_filename = page.create(content=content)
    subpage_content = "This it the subpage content"
    subpage_title = "Sub page original title"
    sub_page = Page(subpage_title, md_filename)
    sub_page_md_path = sub_page.create(subpage_content)
    subpage_content = "Now updated sub page content"
    sub_page_md_path_updated = sub_page.update(
        subpage_content, sub_page.title, sub_page.title + " changed"
    )
    assert sub_page_md_path_updated.exists()
    with open(sub_page_md_path_updated, "r") as md_file:
        md_content = md_file.read()
    assert md_content == subpage_content
    assert sub_page_md_path.exists() is False
    # Check if the title was updated
    index = IndexHandling()
    index.load_index()
    assert (
        index.index[page.index_title]["sub_pages"][sub_page.index_title]["title"]
        == sub_page.title
    )
    # Assert the md_file was updated and is updated to the same value in the index file
    assert (
        index.index[page.index_title]["sub_pages"][sub_page.index_title]["md"]
        == sub_page.md_file
    )


def test_get_page_from_endpoint(client, temp_dir):
    """Test getting a page from an endpoint."""
    os.environ["MD_PATH"] = temp_dir
    content = "This is a test page."
    title = "A nice test page"
    page = Page(title)
    page_filepath = page.create(content)
    url = page.url
    response = client.get(url)
    assert page_filepath.exists()
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
    # Create a mock S3 client
    mock_s3_client = MagicMock()

    # Patch boto3.client to return our mock
    with patch("boto3.client", return_value=mock_s3_client):
        # Set variables to dry
        the_filename = "TestPage.md"
        bucket = os.environ["BUCKET_NAME"]
        test_file_path = Path(the_filename)
        object_name = the_filename

        # Initialize the class
        s3 = S3Handler()

        # Create a test file
        with open(test_file_path, "w", encoding="utf-8") as file:
            file.write("This is a test file.")

        # Upload the test file
        s3.upload_file(str(test_file_path), the_filename, bucket)

        # Check if the file exists in S3
        # Assert the S3 client's upload_file method was called with correct parameters
        mock_s3_client.upload_file.assert_called_once_with(
            Bucket=bucket, Key=the_filename, Filename=the_filename
        )


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
    assert response.json["url"] == f"/pages/{pagename.lower()}"
    assert response.json["message"] == f"Page {pagename} created successfully"


def test_endpoint_for_creating_a_page_adds_to_index(client, random_id, temp_dir):
    """Test that the page is added to the index after creation."""
    os.environ["MD_PATH"] = temp_dir
    content = "This is a test page."
    pagename = random_id
    pagename = pagename.lower()
    response = client.post(
        f"/pages/create/{pagename}", data={"content": content, "title": pagename}
    )
    assert response.status_code == 200
    index = IndexHandling()
    index.load_index()
    assert pagename in index.index
    assert index.index[pagename]["md"] == f"{pagename}.md"


def test_endpoint_for_updating_content(client, random_id):
    """Tests the endpoint implementing update of content for a page"""
    # We will mock the s3 client for downloading and uploading the file from S3
    mock_s3_client = MagicMock()

    # We need a temporary directory for test pages to be created
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir

        # Patch boto3.client to return our mock
        with patch("boto3.client", return_value=mock_s3_client):
            s3 = S3Handler()

            # Test downloading a file
            bucket = "test-bucket"
            s3_key = "test_file.md"
            local_path = "downloaded_file.md"

            # Some content and a title to create the page first
            current_content = "Some content"
            page_name = "flashy test page"
            page_index_filename = "flashy-test-page"
            page_md_filename = page_index_filename + ".md"

            # Create the page with the content
            response = client.post(
                f"/pages/create/{page_index_filename}",
                data={"content": current_content, "title": page_name},
            )

            assert Path(temp_dir, page_md_filename).exists()

            # Set content to something new, so we can test updating works
            new_content = current_content + " and more content"

            # Update the page
            response = client.post(
                f"/pages/update/{page_index_filename}",
                data={"content": new_content, "title": page_name},
            )
            assert response.status_code == 200

            # Let's check the file was updated
            with open(Path(temp_dir, page_md_filename)) as page_file:
                file_content = page_file.read()
            assert new_content == file_content


def test_endpoint_for_updating_content_in_subpage(client, random_id):
    """Tests the endpoint implementing update of content for a page"""
    # We will mock the s3 client for downloading and uploading the file from S3
    mock_s3_client = MagicMock()

    # We need a temporary directory for test pages to be created
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir

        # Patch boto3.client to return our mock
        with patch("boto3.client", return_value=mock_s3_client):
            s3 = S3Handler()

            # Test downloading a file
            bucket = "test-bucket"
            s3_key = "test_file.md"
            local_path = "downloaded_file.md"

            # Some content and a title to create the page first
            current_content = "Some content"
            page_name = "flashy test page"
            page_index_filename = "flashy-test-page"
            page_md_filename = page_index_filename + ".md"

            # Create the page with the content
            response = client.post(
                f"/pages/create/{page_index_filename}",
                data={"content": current_content, "title": page_name},
            )

            assert Path(temp_dir, page_md_filename).exists()

            # Now create a sub page
            sub_page_content = "This is a sub page"
            sub_page_title = "sub page"
            response = client.post(
                f"/pages/create/{page_index_filename}/{sub_page_title}",
                data={"content": sub_page_content, "title": sub_page_title},
            )
            assert response.status_code == 200

            # Set content to something new, so we can test updating works
            updated_content = current_content + " and more content"

            # Update the page
            response = client.post(
                f"/pages/update/{page_index_filename}/sub-page",
                data={"content": updated_content, "title": sub_page_title},
            )
            assert response.status_code == 200

            # Let's check the file was updated
            with open(
                Path(temp_dir, f"{page_index_filename}.sub-page.md")
            ) as page_file:
                file_content = page_file.read()
            assert updated_content == file_content


def test_normalize_md_filename_from_title():
    """Test the normalization of a title to a markdown filename."""
    title = "This is a test page"
    page = Page(title)
    expected_filename = "this-is-a-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_md_filename_from_title_with_special_chars():
    """Test the normalization of a title with special characters to a markdown filename."""
    title = "This is a test page!@#$%^&*()"
    page = Page(title)
    expected_filename = "this-is-a-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_md_filename_from_title_with_spaces_start_and_end():
    """Test the normalization of a title with spaces to a markdown filename."""
    title = " This is a test page "
    page = Page(title)

    expected_filename = "this-is-a-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_md_filename_from_title_with_dots_and_underscores():
    """Test the normalization of a title with dots and underscores to a markdown filename."""
    title = "This.is_a test.page"
    page = Page(title)
    expected_filename = "this-is-a-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_md_filename_from_title_with_double_dashes():
    """Test the normalization of a title with double dashes to a markdown filename."""
    title = "This--is--a--test--page"
    page = Page(title)
    expected_filename = "this-is-a-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_md_filename_from_title_with_leading_and_trailing_dashes():
    """Test the normalization of a title with leading and trailing dashes to a markdown filename."""
    title = "--This is a test page--"
    page = Page(title)
    expected_filename = "this-is-a-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_md_filename_with_path():
    """Test the normalization of a title with path to a markdown filename."""
    title = "This is a test page/this is a sub test page"
    page = Page(title)
    expected_filename = "this-is-a-test-page.this-is-a-sub-test-page.md"
    assert page.normalize_md_filename(title) == expected_filename


def test_normalize_title_of_sub_page_with_path():
    """Test the normalization of a title with path to a markdown filename."""
    title = "This is a test page/this is a sub test page"
    page = Page(title)
    expected_filename = "this-is-a-test-page.this-is-a-sub-test-page"
    assert page.normalize_md_filename(title, drop_md=True) == expected_filename


def test_url_from_md_filename(temp_dir):
    """Test getting a url for a page based on the normalized title"""
    os.environ["MD_FILE"] = temp_dir
    title = "This is a test page"
    page = Page(title)
    title = "This is a test page"
    expected_url = "/pages/this-is-a-test-page"
    assert page.generate_url(page.md_file) == expected_url


def test_url_from_md_filename_subpage():
    """Test getting a url for a sub page"""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_FILE"] = temp_dir
        main_page_title = "This is the main page"
        sub_page_title = "This is a test page"
        main_page = Page(main_page_title)
        main_page_md = main_page.create("some content")
        sub_page = Page(sub_page_title, main_page_md)
        sub_page_md = sub_page.create("Sub page Content")
        expected_url = f"/pages/{sub_page_md.name.replace('.md', '').replace('.', '/')}"
        assert sub_page.generate_url(sub_page.md_file) == expected_url


def test_endpoint_for_save_button_md_editor(client, random_id):
    """Test the endpoint for creating a page."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        pagename = random_id
        response = client.post(
            "/pages/save", data={"content": content, "title": pagename}
        )
    assert response.status_code == 200
    assert response.json["title"] == pagename
    assert response.json["url"] == f"/pages/{pagename.lower()}"
    assert response.json["message"] == f"Page {pagename} created successfully"


def test_delete_page(random_id):
    """Test the page class method for deleting a page."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        pagename = random_id
        page = Page(pagename)
        page.create(content)
        page.delete()
        assert not Path(temp_dir, f"{pagename}.md").exists()
        # Check if the page was removed from the index
        index = IndexHandling()
        index.load_index()
        assert pagename not in index.index
        # Check if the page was removed from the index file
        index_file = Path(temp_dir, "pages_index.yaml")
        with open(index_file, "r", encoding="utf-8") as file:
            index_content = file.read()
        assert pagename not in index_content


def test_delete_sub_page(random_id):
    """Test the page class method for deleting a sub page."""
    with TemporaryDirectory() as temp_dir:
        os.environ["MD_PATH"] = temp_dir
        content = "This is a test page."
        main_page_title = "This is my test page"
        page = Page(main_page_title)
        main_page_file = page.create(content)
        sub_page_title = "This is my sub test page"
        sub_page_content = "This is a sub test page."
        sub_page = Page(sub_page_title, main_page_file.name)
        sub_page.create(sub_page_content)
        sub_page.delete()
        assert not Path(temp_dir, f"{main_page_title}.{sub_page_title}.md").exists()
