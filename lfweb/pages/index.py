"""Class for index handling."""

import yaml


class IndexHandling:
    """Class for index handling."""

    def __init__(self, index_file: str = "lfweb/pages_index.yaml") -> None:
        """Initialize the Index object."""
        self.index_file = index_file
        self.index = self.load_index()

    def load_index(self) -> dict:
        """Load the index."""
        with open(self.index_file, encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def add(self, md_file: str, title: str, url) -> None:
        """Add a page to the index."""
        self.index[title] = {"md": md_file, "title": title, "url": url}
        with open(self.index_file, "w", encoding="utf-8") as file:
            yaml.dump(self.index, file)

    def add_sub_page(self, title: str, sub_title: str, md_file: str, url: str) -> None:
        """Add a sub page to the index."""
        self.index[title]["sub_pages"] = {
            sub_title: {"md": md_file, "title": sub_title, "url": url}
        }
        with open(self.index_file, "w", encoding="utf-8") as file:
            yaml.dump(self.index, file)

    def get_sub_pages(self, title: str) -> dict:
        """Get sub pages from the index."""
        # Get 'title" from self.index, if not found, return empty dict
        # Get "sub_pages" from the result of the previous step, if not found, return empty dict
        return self.index.get(title, {}).get("sub_pages", {})
