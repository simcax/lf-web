"""Tests for the index of pages."""

from pathlib import Path

import yaml

from lfweb.pages.index import IndexHandling


def test_load_index():
    """Test loading the index."""
    index_file = "lfweb/pages/pages_index.yaml"
    index_content = {
        "forside": {"md": "index.md", "title": "index", "url": "/"},
        "about": {"md": "about.md", "title": "about", "url": "/about"},
    }
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content, file)
    index = IndexHandling(index_file)
    assert index.index == index_content
    Path(index_file).unlink()


def test_add_page_to_index():
    """Test adding a page to the index."""
    index_file = "lfweb/pages/pages_index.yaml"
    index_content = {
        "forside": {"md": "index.md", "title": "index", "url": "/"},
        "about": {"md": "about.md", "title": "about", "url": "/about"},
    }
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content, file)
    index = IndexHandling(index_file)
    index.add("test.md", "test", "/test")
    index_content["test"] = {"md": "test.md", "title": "test", "url": "/test"}
    assert index.index == index_content
    Path(index_file).unlink()


def test_add_sub_page_to_index():
    """Test adding a sub page to the index."""
    index_file = "lfweb/pages/pages_index.yaml"
    index_content = {
        "forside": {"md": "index.md", "title": "index", "url": "/"},
        "about": {"md": "about.md", "title": "about", "url": "/about"},
        "test": {"md": "test.md", "title": "test", "url": "/test"},
    }
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(index_content, file)
    index = IndexHandling(index_file)
    index.add("test.md", "test", "/test")
    index.add_sub_page("test", "subpage_title", "sub.md", "/sub")
    index_content["test"]["sub_pages"] = {
        "subpage_title": {
            "md": "sub.md",
            "title": "subpage_title",
            "url": "/sub",
        }
    }
    assert index.index == index_content
    Path(index_file).unlink()


def test_get_sub_pages_from_index():
    """Test getting sub pages from the index."""
    index_file = "lfweb/pages/pages_index.yaml"
    test_page = {
        "md": "test.md",
        "title": "test",
        "url": "/test",
        "sub_pages": {
            "md": "sub.md",
            "title": "subpage_title",
            "url": "/sub",
        },
    }
    index_content = {
        "forside": {"md": "index.md", "title": "index", "url": "/"},
        "about": {"md": "about.md", "title": "about", "url": "/about"},
        "test": test_page,
    }
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(
            index_content,
            file,
        )
    index = IndexHandling(index_file)
    assert index.get_sub_pages("test") == test_page["sub_pages"]
    Path(index_file).unlink()


def test_get_sub_pages_from_index_no_sub_pages():
    """Test getting sub pages from the index with no sub pages."""
    index_file = "lfweb/pages/pages_index.yaml"
    index_content = {
        "forside": {"md": "index.md", "title": "index", "url": "/"},
        "about": {"md": "about.md", "title": "about", "url": "/about"},
        "test": {"md": "test.md", "title": "test", "url": "/test"},
    }
    with open(index_file, "w", encoding="utf-8") as file:
        yaml.dump(
            index_content,
            file,
        )
    index = IndexHandling(index_file)
    assert index.get_sub_pages("test") == {}
    Path(index_file).unlink()
