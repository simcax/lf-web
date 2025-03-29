"""Tests for the doorcount scraper"""

from unittest.mock import patch

import lfweb.utils.doorcount_scrape as ds


def test_parse_data(doorcount_html):
    """Test that we can parse the doorcount page"""
    with patch("lfweb.utils.doorcount_scrape.requests.get") as mock_get:
        mock_get.return_value.text = doorcount_html
        scraper = ds.DoorCountScraper("http://example.com")
        page = scraper.fetch_page()
        data = scraper.parse_data(page)
        assert data is not None
        assert len(data.get("arrived_intervals").keys()) > 0
        assert data.get("arrived_intervals").get("75_minutes") == 3


def test_doorcount_scraper_fails(doorcount_html):
    """Test that the scraper fails gracefully"""
    with patch("lfweb.utils.doorcount_scrape.requests.get") as mock_get:
        mock_get.return_value.text = None
        scraper = ds.DoorCountScraper("http://example.com")
        page = scraper.fetch_page()
        data = scraper.parse_data(page)
        assert data == {}
