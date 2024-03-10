"""Tests for the pages module."""

from pathlib import Path

from lfweb.pages.index import IndexHandling
from lfweb.pages.page import Page


def test_create_page():
    """Test creating a page."""
    content = "This is a test page."
    page = Page("TestPage.md", "TestPage")
    page.create(content)
    with open("TestPage.md", encoding="utf-8") as file:
        assert file.read() == content


def test_render_page():
    """Test rendering a page."""
    content = "This is a test page."
    page = Page("TestPage.md", "TestPage")
    page.create(content)
    assert page.render() == '<p class="pb-4 text-normal">This is a test page.</p>'


def test_get_page_from_endpoint(client):
    """Test getting a page from an endpoint."""
    content = "This is a test page."
    page = Page("TestPage.md", "TestPage")
    page.create(content)
    index_file = "lfweb/pages/current_pages.yaml"
    index = IndexHandling(index_file)
    index.add("TestPage.md", "TestPage", "/pages/TestPage")
    response = client.get("/pages/TestPage")
    test_page = Path("TestPage.md")
    assert test_page.exists()
    assert response.status_code == 200
    assert content in response.data.decode("utf-8")
