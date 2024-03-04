"""Module to style the page with Tailwind CSS."""

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class TailwindExtension(Extension):
    """A class to style the page with Tailwind CSS."""

    def extendMarkdown(self, md):
        """Extend the markdown class."""
        md.treeprocessors.register(TailwindTreeProcessor(md), "tailwind", 20)


class TailwindTreeProcessor(Treeprocessor):
    """Walk the root node and modify any discovered tag"""

    classes = {
        "a": "underline text-blue-700 hover:text-blue-500",
        "p": "pb-4 text-normal",
        "h1": "text-4xl",
        "h2": "text-3xl",
        "h3": "text-2xl",
        "h4": "text-xl",
        "code": "font-sans indent-1 italic border-spacing-x-2 rounded-xl bg-white-200 shadow-md shadow-white-500/50",  # pylint: disable=line-too-long
        "img": "rounded-lg size-64",
    }

    def run(self, root):
        for node in root.iter():
            tag_classes = self.classes.get(node.tag)
            if tag_classes:
                node.attrib["class"] = tag_classes
