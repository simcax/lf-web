from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger


class DoorCountScraper:
    """
    A class to scrape member count data from foreninglet.dk
    """

    def __init__(self, url: str):
        """
        Initialize the scraper with the target URL

        Args:
            url: The URL to scrape data from
        """
        self.url = url
        self.logger = logger

    def fetch_page(self) -> Optional[str]:
        """
        Fetch the webpage content

        Returns:
            The HTML content of the page or None if request fails
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch page: {e}")
            return None

    def parse_data(self, html_content: str) -> Dict[str, Any]:
        """
        Parse the HTML content to extract relevant information

        Args:
            html_content: The HTML content to parse

        Returns:
            A dictionary containing the extracted data
        """
        if not html_content:
            return {}

        soup = BeautifulSoup(html_content, "html.parser")
        result = {}

        try:
            # Extract time intervals and counts
            arrived_data = {}
            time_intervals = soup.find_all("br")

            for interval in time_intervals:
                if interval.previous_sibling and isinstance(
                    interval.previous_sibling, str
                ):
                    text = interval.previous_sibling.strip()
                    if "minutter:" in text:
                        parts = text.split(":")
                        if len(parts) == 2:
                            minutes = parts[0].replace("minutter", "").strip()
                            count = parts[1].strip()
                            arrived_data[f"{minutes}_minutes"] = int(count)

            result["arrived_intervals"] = arrived_data

            # Extract the last updated timestamp
            updated_element = soup.find("i")
            if updated_element:
                update_text = updated_element.text.strip()
                if "Senest opdateret:" in update_text:
                    result["last_updated"] = update_text.replace(
                        "Senest opdateret:", ""
                    ).strip()

        except Exception as e:
            self.logger.error(f"Error parsing HTML content: {e}")

        return result

    def get_door_count(self) -> Dict[str, Any]:
        """
        Main method to get door count data

        Returns:
            A dictionary with the scraped data
        """
        html_content = self.fetch_page()
        if not html_content:
            return {"error": "Failed to fetch page"}

        return self.parse_data(html_content)
