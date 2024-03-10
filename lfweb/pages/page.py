"""Module for the Page class."""

import markdown

from .tailwind import TailwindExtension


class Page:
    """A class representing a web page."""

    def __init__(self, md_file: str = None, title: str = None):
        """Initialize the Page object."""
        self.md_file = md_file
        self.title = title

    def render(self):
        """Render the page."""
        try:
            with open(self.md_file, encoding="utf-8") as file:
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
            return "Page content not found."

    def create(self, content: str):
        """Create a page."""
        with open(self.md_file, "w", encoding="utf-8") as file:
            file.write(content)
