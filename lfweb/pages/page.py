"""Module for the Page class."""

import os
from pathlib import Path

import markdown
from loguru import logger

from lfweb.pages.index import IndexHandling

from .tailwind import TailwindExtension


class Page:
    """
    A class representing a web page.
    ::param:: title: The title of the page. This makes the bases for the page md filename. It will be normalized to a filename
    ::param:: parent_md_file: The parent markdown file. This is used to create sub pages.

    ::returns:: None
    ::raises:: None
    """

    def __init__(self, title: str = None, parent_md_file: str = None):
        """Initialize the Page object."""
        if parent_md_file:
            if isinstance(parent_md_file, str):
                parent_md_file = Path(parent_md_file)
            full_title = f"{parent_md_file.name.replace('.md', '')}/{title}"
        else:
            full_title = title
        # Normalize the title to a filename - this is the full filename of the md file
        self.md_file = self.normalize_md_filename(full_title)
        # The title will be added as-is in the yaml index file
        self.title = title
        self.index_title = self.normalize_md_filename(title, True)
        self.index_title_full = self.normalize_md_filename(full_title, True)
        # Take the path to the markdown files from the environment variable
        self.md_file_path = os.environ.get("MD_PATH")
        # Set the path to the markdown file including the md filename
        self.md_page_file_path = Path(self.md_file_path, self.md_file)
        # Set the url
        self.url = self.generate_url(self.md_file)

    def render(self):
        """Render the page."""
        try:
            # Read the markdown file
            with open(self.md_page_file_path, encoding="utf-8") as file:
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
            logger.critical(
                f"Markdown file path: {self.md_page_file_path.name} not found"
            )
            return "Page content not found."

    def create(self, content: str):
        """Create a page."""
        try:
            with open(self.md_page_file_path, "w", encoding="utf-8") as file:
                file.write(content)
            logger.info(f"Page {self.md_file} created successfully.")
            # Update the index
            index = IndexHandling()
            index.add(self.md_file, self.title, self.url)
        except Exception as e:
            logger.error(f"Error creating page {self.md_file}: {e}")
            raise e
        return self.md_page_file_path

    def update(
        self,
        content: str,
        original_title: str,
        new_title: str = None,
    ) -> str:
        """
        Updates the content in an existing md file

        ::param:: content: The content to be written to the md file
        ::param:: original_title: The original title of the page
        ::param:: new_title: The new title of the page
        """
        try:
            with open(self.md_page_file_path, "w", encoding="utf-8") as page_file:
                page_file.write(content)
                # Set the md file variable to be returned
                new_md_file_path = self.md_page_file_path
            logger.info(f"Updated content in {self.md_file}")
            if new_title:
                # Update the title in the index
                new_index_title = self.normalize_md_filename(new_title, True)
                original_title_to_be_replaced = self.index_title

                # Set the current md file path
                current_md_file_path = self.md_page_file_path
                # Set the new md file path
                new_md_file_path = Path(
                    str(current_md_file_path).replace(
                        original_title_to_be_replaced,
                        new_index_title,
                    )
                )

                new_title_md_file = self.md_file.replace(
                    original_title_to_be_replaced,
                    new_index_title,
                )
                new_index_title_full = self.index_title_full.replace(
                    original_title_to_be_replaced,
                    new_index_title,
                )
                new_url = self.generate_url(new_index_title_full)
                # Move the md file to the new name
                self.md_page_file_path.rename(new_md_file_path)
                # Update the md file name in the index
                index = IndexHandling()
                files_to_rename = index.update_index(
                    self.index_title,
                    new_title,
                    new_index_title,
                    new_md_file_path.name,
                    new_url,
                )
                # Rename any sub page md files needed
                for file in files_to_rename:
                    old_file = Path(self.md_file_path, file["old"])
                    new_file = Path(self.md_file_path, file["new"])
                    if old_file.exists():
                        old_file.rename(new_file)
                        logger.info(f"Renamed {old_file} to {new_file}")
                    else:
                        logger.warning(f"{old_file} does not exist")
                        raise FileExistsError(
                            f"{old_file} does not exist. Can't rename file."
                        )
                # Update the page with the new info
                self.md_file = new_title_md_file
                self.md_page_file_path = new_md_file_path
                self.title = new_title
                self.url = new_url
                self.index_title = new_index_title
                self.index_title_full = new_index_title_full
        except FileExistsError as e:
            logger.error(
                f"{self.md_page_file_path} does not exist. Can't update non existing file. {e}"
            )
            return ""
        return new_md_file_path

    def md_content(self) -> str:
        """Get the content of the markdown file."""
        try:
            with open(self.md_page_file_path, encoding="utf-8") as file:
                md = file.read()
            return md
        except FileNotFoundError:
            logger.critical(
                f"Markdown file path: {self.md_page_file_path.name} not found"
            )
            return "Page content not found."

    def normalize_md_filename(self, title: str, drop_md: bool = False) -> str:
        """Normalize the markdown filename."""
        # Normalize the title to a filename
        title = title.replace(" ", "-").lower()
        # Replace . and _ with -
        title = title.replace(".", "-").replace("_", "-")
        # Convert / to . (for path segments)
        title = title.replace("/", ".")
        # Remove special characters
        title = "".join(e for e in title if e.isalnum() or e in ["-", "."])
        # Remove double dashes
        title = title.replace("--", "-")
        # Remove leading and trailing dashes
        title = title.strip("-")
        # Add .md unless drop_md
        title = title if drop_md else title + ".md"
        return title

    def generate_url(self, title: str) -> str:
        """Takes a normalized title and generates a url"""
        base_url = "/pages"
        # Remove the .md
        base_title = title.replace(".md", "")
        # Concatenate the normalized title and revert . to slash
        base_title = base_title.replace(".", "/")
        # Generate the full url
        full_url = f"{base_url}/{base_title}"
        return full_url

    def delete(self):
        """Delete the page."""
        try:
            os.remove(self.md_page_file_path)
            logger.info(f"Page {self.md_file} deleted successfully.")
            # Update the index
            index = IndexHandling()
            index.delete_index_entry(self.md_file)
        except FileNotFoundError:
            logger.error(f"Error deleting page {self.md_file}: file not found")
            raise FileNotFoundError(f"File {self.md_page_file_path} not found")
        except Exception as e:
            logger.error(f"Error deleting page {self.md_file}: {e}")
            raise e
        return self.md_page_file_path
