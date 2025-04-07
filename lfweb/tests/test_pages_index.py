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
