"""Tests for the index of pages."""

import os
from pathlib import Path

import yaml

from lfweb.pages.index import IndexHandling


def test_load_index(index_content_basic, temp_dir):
    """Test loading the index."""
    os.environ["MD_PATH"] = temp_dir
    index_file = Path(temp_dir, "pages_index.yaml")
    # Create the index file with basic content
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content_basic, file)
    index = IndexHandling()

    assert index.index == index_content_basic
    Path(index_file).unlink()


def test_add_page_to_index(index_content_basic, temp_dir):
    """Test adding a page to the index."""
    os.environ["MD_PATH"] = temp_dir
    index_file = Path(temp_dir, "pages_index.yaml")
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content_basic, file)
    index = IndexHandling()
    index.add("test.md", "test", "/test")

    index_content_basic["test"] = {"md": "test.md", "title": "test", "url": "/test"}
    assert index.index == index_content_basic


def test_add_sub_page_to_index(index_content_basic_2, temp_dir):
    """Test adding a sub page to the index."""
    os.environ["MD_PATH"] = temp_dir
    index_file = Path(temp_dir, "pages_index.yaml")
    # Create the index file with basic content
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content_basic_2, file)
    index = IndexHandling()
    sub_page_md_file = "test.sub-test-page.md"
    title = "sub test page"
    url = "/test/sub-test-page"
    index.add(sub_page_md_file, title, "/test")
    index.add_sub_page("test", "subpage_title", "sub.md", "/sub")
    index_content_basic_2["test"]["sub_pages"] = {
        "subpage_title": {
            "md": "sub.md",
            "title": "subpage_title",
            "url": "/sub",
        }
    }
    assert index.index == index_content_basic_2


def test_get_sub_pages_from_index(temp_dir, index_content_basic_2):
    """Test getting sub pages from the index."""
    os.environ["MD_PATH"] = temp_dir
    index_file = Path(temp_dir, "pages_index.yaml")
    # Define the test page with sub pages
    sub_page = {
        "subpage_title": {
            "md": "sub.md",
            "title": "subpage_title",
            "url": "/sub",
        }
    }
    index_content_basic_2["test"]["sub_pages"] = sub_page
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(
            index_content_basic_2,
            file,
        )
    index = IndexHandling()
    assert index.get_sub_pages("test") == sub_page


def test_get_sub_pages_from_index_no_sub_pages(temp_dir, index_content_basic):
    """Test getting sub pages from the index with no sub pages."""
    os.environ["MD_PATH"] = temp_dir
    index_file = Path(temp_dir, "pages_index.yaml")
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(
            index_content_basic,
            file,
        )
    index = IndexHandling()
    assert index.get_sub_pages("test") == {}


def test_update_index_entry_having_a_sub_page(temp_dir, index_content_basic_2):
    """Test updating an index entry having a sub page."""
    os.environ["MD_PATH"] = temp_dir
    index_file = Path(temp_dir, "pages_index.yaml")
    # Create the index file with basic content
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content_basic_2, file)
    index = IndexHandling()
    # Create a new main page
    main_title = "Main page title"
    main_md_file = "main-page-title.md"
    main_url = "/main-page-title"
    index.add(
        main_md_file,
        main_title,
        main_url,
    )
    # Create a new sub page
    sub_title = "Sub page title"
    sub_md_file = "main-page-title.sub-page-title.md"
    sub_url = "main-page-title/sub-page-title"
    index.add(
        sub_md_file,
        sub_title,
        sub_url,
    )
    # Update the main page title
    original_index_title = "main-page-title"
    new_title = "New main page title"
    new_index_title = "new-main-page-title"
    new_md_file = "new-main-page-title.md"
    new_url = "/new-main-page-title"
    index.update_index(
        original_index_title, new_title, new_index_title, new_md_file, new_url
    )
    # Check if the main page is updated
    assert index.index[new_index_title] == {
        "md": new_md_file,
        "title": new_title,
        "url": new_url,
        "sub_pages": {
            "sub-page-title": {
                "md": sub_md_file.replace("main-page-title", new_index_title),
                "title": sub_title,
                "url": sub_url,
            }
        },
    }
    # Check if the sub page still exists
    assert index.index[new_index_title]["sub_pages"]["sub-page-title"] == {
        "md": sub_md_file.replace("main-page-title", new_index_title),
        "title": sub_title,
        "url": sub_url,
    }
