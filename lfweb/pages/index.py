"""Class for index handling."""

import os
from pathlib import Path

import yaml


class IndexHandling:
    """Class for index handling."""

    def __init__(self, index_file: str = None) -> None:
        """Initialize the Index object."""
        # We set the index filename to a default value
        index_filename = "pages_index.yaml"
        # The MD_PATH should be set in the environment
        # But then the index_file should not be set explicitely
        self.md_path = os.environ.get("MD_PATH")
        if self.md_path and index_file is None:
            self.index_file = Path(self.md_path, index_filename)
        # Only if the self.MD_PATH is not set, the index_file parameter will be considered
        elif index_file is not None:
            self.index_file = index_file
        elif self.md_path and index_file:
            raise ValueError(
                f"Please set EITHER the self.MD_PATH env var ({self.md_path}) OR the index_file parameter ({index_file})"
            )
        else:
            raise ValueError(
                "Index file not set, both self.MD_PATH and index_file is empty"
            )
        self.index = self.load_index()

    def load_index(self) -> dict:
        """Load the index."""
        try:
            index = {}
            # Check if the index file exists
            if not os.path.exists(self.index_file):
                # If it does not exist, create an empty index
                with open(self.index_file, "w", encoding="utf-8") as file:
                    yaml.dump({}, file)
                return {}
            # If it exists, load the index from the file
            # If the file is empty, create an empty index
            if os.stat(self.index_file).st_size == 0:
                with open(self.index_file, "w", encoding="utf-8") as file:
                    yaml.dump({}, file)
                return {}
            with open(self.index_file, encoding="utf-8") as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            # If the index file does not exist, create an empty index
            with open(self.index_file, "w", encoding="utf-8") as file:
                yaml.dump({}, file)
            return {}

    def add(self, md_file: str, title: str, url) -> None:
        """Add a page to the index."""
        # Detect if it is a sub page by counting number of . - 2 . = sub page, 1 = main page
        sub_index_entry = None
        if md_file.count(".") == 2:
            # If it is a sub page, the page should be added as a sub page
            sub_index_entry = md_file.replace(".md", "").split(".")[1]
        index_entry = md_file.replace(".md", "").split(".")[0]
        if sub_index_entry:
            try:
                # If the index entry exists, add the sub page to it
                # If there is no sub pages key, create it
                if self.index.get(index_entry).get("sub_pages") is None:
                    self.index[index_entry]["sub_pages"] = {}
                    self.index[index_entry]["sub_pages"] = {
                        sub_index_entry: {"md": md_file, "title": title, "url": url}
                    }
                else:
                    self.index[index_entry]["sub_pages"][sub_index_entry] = {
                        "md": md_file,
                        "title": title,
                        "url": url,
                    }
            except KeyError:
                # If the index entry does not exist, create it
                self.index[index_entry] = {
                    "sub_pages": {
                        sub_index_entry: {"md": md_file, "title": title, "url": url}
                    },
                }
        else:
            self.index[index_entry] = {"md": md_file, "title": title, "url": url}
        with open(self.index_file, "w", encoding="utf-8") as file:
            yaml.dump(self.index, file)

    def add_sub_page(self, title: str, sub_title: str, md_file: str, url: str) -> None:
        """Add a sub page to the index."""
        index_entry = title.replace(".md", "").split(".")[0]

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

    def update_index(
        self,
        original_index_title: str,
        new_title: str,
        new_index_title: str,
        new_md_file: str,
        new_url: str,
    ) -> None:
        """Update the index."""
        sub_index_entry = None
        md_files_to_rename = []
        # Update the index with the new title and md file
        if new_md_file.count(".") == 2:
            index_entry = new_md_file.replace(".md", "").split(".")[0]
            sub_index_entry = original_index_title
        else:
            index_entry = original_index_title

        if index_entry in self.index:
            # Check if the original title is a sub page
            if (
                sub_index_entry is not None
                and sub_index_entry in self.index[index_entry]["sub_pages"]
            ):
                # If it is a sub page, update the sub page
                self.index[index_entry]["sub_pages"][new_index_title] = {
                    "md": new_md_file,
                    "title": new_title,
                    "url": new_url,
                }
                self.index[index_entry]["sub_pages"].pop(sub_index_entry)
            else:
                self.index[new_md_file.replace(".md", "")] = {
                    "md": new_md_file,
                    "title": new_title,
                    "url": new_url,
                }
                # move the sub pages to the new index title
                if self.index.get(original_index_title) is not None:
                    self.index[new_md_file.replace(".md", "")][
                        "sub_pages"
                    ] = self.index[original_index_title].get("sub_pages")
                if self.index[original_index_title].get("sub_pages", {}) is not None:
                    # Replace the old main md index name in the sub page md files path
                    for sub_page in self.index[original_index_title].get(
                        "sub_pages", {}
                    ):
                        original_sub_page_md_file = self.index[original_index_title][
                            "sub_pages"
                        ][sub_page]["md"]
                        new_sub_page_md_file = original_sub_page_md_file.replace(
                            original_index_title, new_index_title
                        )
                        # Update the sub page md file name
                        self.index[new_md_file.replace(".md", "")]["sub_pages"][
                            sub_page
                        ]["md"] = new_sub_page_md_file
                        # Add the sub page md file to the list of files to rename

                        md_files_to_rename.append(
                            {
                                "old": original_sub_page_md_file,
                                "new": new_sub_page_md_file,
                            }
                        )
                        # Update the url of the sub page
                        self.index[new_md_file.replace(".md", "")]["sub_pages"][
                            sub_page
                        ]["url"] = (new_url + "/" + sub_page)
                # Remove the old title from the index
                self.index.pop(original_index_title)
        else:
            raise ValueError(f"Title {original_index_title} not found in index")
        with open(self.index_file, "w", encoding="utf-8") as file:
            yaml.dump(self.index, file)
        return md_files_to_rename

    def delete_index_entry(self, title: str) -> None:
        """
        Delete an index entry.

        ::param:: title: The full name of the md file of the page to be removed from the index
        ::return:: True if the entry was deleted successfully
        ::raises:: ValueError: If the title is not found in the index
        """
        # First check if this is a sub page
        sub_index_entry = None
        if title.count(".") == 2:
            # If it is a sub page, the page should be deleted as a sub page
            sub_index_entry = title.replace(".md", "").split(".")[1]
            index_entry = title.replace(".md", "").split(".")[0]
        else:
            index_entry = title.replace(".md", "")
        # If it is a sub page, delete the sub page
        if sub_index_entry:
            try:
                # If the index entry exists, delete the sub page from it
                # If there is no sub pages key, create it
                if self.index.get(index_entry).get("sub_pages") is None:
                    raise ValueError(f"Sub page {sub_index_entry} not found in index")
                else:
                    self.index[index_entry]["sub_pages"].pop(sub_index_entry)
            except KeyError:
                # If the index entry does not exist, raise an error
                raise ValueError(f"Title {index_entry} not found in index")
        else:
            # If it is not a sub page, delete the index entry
            # Check if the index entry exists
            if self.index.get(index_entry) is None:
                raise ValueError(f"Title {index_entry} not found in index")
            else:
                # If it does, delete it
                self.index.pop(index_entry)

        # Write the index back to the file
        with open(self.index_file, "w", encoding="utf-8") as file:
            yaml.dump(self.index, file)
        return True
