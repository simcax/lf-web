"""Editor routes for the web application.
This module contains the routes for the editor page, where users can create and edit pages.
It includes the following routes:
- /editor/do/<action>: Renders the editor page for creating or editing a page.
- /editor/add-link: Adds a link to the page.
"""

from flask import Blueprint, jsonify, render_template, request

from lfweb.pages.index import IndexHandling
from lfweb.pages.page import Page

bp = Blueprint("route_editor", __name__, url_prefix="/editor")
from loguru import logger


@bp.route("/do/<action>", methods=["GET", "POST"])
def editor(action: str) -> str:
    """
    Renders the editor page
    """
    if action not in ("create", "edit"):
        logger.error(f"Action {action} not found")
        return render_template("404.html"), 404
    # Set default values
    sub_page = False
    parent_page = None
    markdown_data = ""
    title = ""
    page_name = ""
    sub_page = bool(request.args.get("type") == "subpage")
    if sub_page:
        parent_page = request.args.get("parent_page")
    if action == "edit":
        page_name = request.args.get("page_name")
        title = request.args.get("title")
        if sub_page:
            page = Page(title, parent_page)
            markdown_data = page.md_content()
            logger.debug(
                f"Loading sub page: {page_name} and parent_page: {parent_page}"
            )
        else:
            page = Page(title)
            markdown_data = page.md_content()
        title = page.title
    return render_template(
        "/snippets/editor.html",
        markdown_data=markdown_data,
        action=action,
        sub_page=sub_page,
        parent_page=parent_page,
        title=title,
        page_name=page_name,
    )


@bp.route("/add-link", methods=["GET", "POST"])
def add_link():
    """
    Adds a link to the page
    """
    if request.method == "POST":
        link = request.args.get("link")
        title = request.args.get("title")
        page_name = request.args.get("page_name")
        sub_page = request.args.get("sub_page")
        if sub_page:
            index = IndexHandling()
            index.load_index()
            parent_md_page_name = index.index.get(page_name).get("md")
            logger.debug(f"Creating sub page: {sub_page}")
        else:
            parent_md_page_name = None
        page = Page(title, parent_md_page_name)
        page.add_link(link)
        return (
            jsonify(
                {
                    "message": f"Link {link} added successfully",
                    "url": page.url,
                    "title": title,
                }
            ),
            200,
        )
    else:
        return render_template("snippets/add_link.html")
