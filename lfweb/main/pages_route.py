"""Module for handling the pages automatically from config file"""

from flask import Blueprint, render_template
from loguru import logger

from lfweb.pages.index import IndexHandling
from lfweb.pages.page import Page

bp = Blueprint("route_pages", __name__, url_prefix="/pages")


@bp.route("/<page>")
@bp.route("/<page>/<sub_page>")
def pages(page: str, sub_page: str = None) -> str:
    """
    Renders the pages
    """
    # We need to load the index here, as it is used to render the pages
    index_file = "lfweb/pages/current_pages.yaml"  # TODO: Move to config
    index = IndexHandling(index_file)
    index.load_index()
    if sub_page:
        page_name = f"{page}/{sub_page}"
        logger.debug(f"Loading sub page: {page_name} and sub_page: {sub_page}")
        logger.debug(f"{index.index.get(page)}")
        if index.index.get(page).get("sub_pages").get(sub_page) is None:
            return render_template("404.html"), 404
        title = index.index.get(page).get("sub_pages").get(sub_page).get("title")
        md = index.index.get(page).get("sub_pages").get(sub_page).get("md")
        page_content = Page(md)
    else:
        if index.index.get(page) is None:
            return render_template("404.html"), 404
        title = index.index.get(page).get("title")
        page_content = Page(index.index[page]["md"])
    logger.info(f"Loading page: {page_name if sub_page else page}")

    return render_template(
        "page.html",
        title=title,
        page_content=page_content.render(),
        pages=index.index,
    )
