"""Module for the Page class."""

import os
from pathlib import Path

import markdown
from loguru import logger

from lfweb.pages.index import IndexHandling

from .tailwind import TailwindExtension


class Page:
    """A class representing a web page."""

    def __init__(self, md_file: str = None, title: str = None):
        """Initialize the Page object."""
        self.md_file = md_file
        self.title = title
        md_file_path = os.environ.get("MD_PATH")
        # Set the path to the markdown file
        self.md_file_path = Path(md_file_path, self.md_file)

    def render(self):
        """Render the page."""
        try:
            # Read the markdown file
            with open(self.md_file_path, encoding="utf-8") as file:
                md = file.read()
            return markdown.markdown(
                md,
                output_format="html5",
                extensions=[TailwindExtension(), "tables", "nl2br"],
                # md = md.replace("<h1>", "<h1 class='text-lg'>")
                # return Markup(
                #     markdown.markdown(md, output_format="html5"),
                #     extensions=["TailwindExtension()"],
            )
        except FileNotFoundError:
            # Log a warning if the file is not found
            logger.critical(f"Markdown file path: {md_file_path.name} not found")
            return "Page content not found."

    def create(self, content: str, url: str = None):
        """Create a page."""
        try:
            with open(self.md_file_path, "w", encoding="utf-8") as file:
                file.write(content)
            logger.info(f"Page {self.md_file} created successfully.")
            # Update the index
            index_file = Path(os.environ.get("MD_PATH"), "current_pages.yaml")
            index = IndexHandling(index_file)
            index.add(self.md_file, self.title, url)
        except Exception as e:
            logger.error(f"Error creating page {self.md_file}: {e}")
            raise e
        return self.md_file_path
