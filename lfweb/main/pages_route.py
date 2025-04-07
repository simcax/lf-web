"""Module for handling the pages automatically from config file"""

import os

from flask import Blueprint, jsonify, render_template, request
from loguru import logger

from lfweb.members.list import Memberdata
from lfweb.pages.index import IndexHandling
from lfweb.pages.page import Page

bp = Blueprint("route_pages", __name__, url_prefix="/pages")
from pathlib import Path

# Set the path to the folder for markdown files
md_file_path = os.environ.get("MD_PATH")
if md_file_path is None:
    logger.warning("MD_PATH not set in environment variables")


@bp.route("/<page>")
@bp.route("/<page>/<sub_page>")
def pages(page: str, sub_page: str = None) -> str:
    """
    Renders the pages
    """
    # We need to load the index here, as it is used to render the pages
    index = IndexHandling()
    index.load_index()
    memberdata = Memberdata()
    if sub_page:
        page_name = f"{page}/{sub_page}"
        logger.debug(f"Loading sub page: {page_name} and sub_page: {sub_page}")
        logger.debug(f"{index.index.get(page)}")
        if index.index.get(page).get("sub_pages").get(sub_page) is None:
            logger.warning(f"Sub page {sub_page} not found in index")
            return render_template("404.html"), 404
        main_page_md = index.index.get(page).get("md")
        sub_page_title = (
            index.index.get(page).get("sub_pages").get(sub_page).get("title")
        )
        page_content = Page(sub_page_title, main_page_md)
    else:
        if index.index.get(page) is None:
            logger.warning(f"Page {page} not found in index")
            return render_template("404.html"), 404
        title = index.index.get(page).get("title")
        page_content = Page(title)
    logger.info(f"Loading page: {page_name if sub_page else page}")

    return render_template(
        "page.html",
        title=title,
        page_content=page_content.render(),
        pages=index.index,
        memberdata=memberdata,
    )


@bp.route("/create/<pagename>", methods=["POST"])
@bp.route("/create/<pagename>/<sub_page>", methods=["POST"])
def create_page(pagename: str, sub_page: str = None) -> str:
    """
    An endpoint which can take content to create a new page
    """
    content = request.form.get("content")
    title = request.form.get("title")

    if sub_page:
        index = IndexHandling()
        index.load_index()
        parent_md_page_name = index.index.get(pagename).get("md")
        logger.debug(f"Creating sub page: {sub_page}")
    else:
        parent_md_page_name = None
    page = Page(title, parent_md_page_name)
    page.create(content)
    return (
        jsonify(
            {
                "message": f"Page {page.title} created successfully",
                "url": page.url,
                "title": title,
            }
        ),
        200,
    )


@bp.route("/update/<page>", methods=["POST"])
@bp.route("/update/<page>/<sub_page>", methods=["POST"])
def update_page_content(page: str, sub_page: str = None) -> str:
    """Updates page content, and stores it in the md file"""

    index = IndexHandling()
    title = request.form.get("title")
    content = request.form.get("content")
    index.load_index()
    if sub_page:
        page_name = f"{page}/{sub_page}"
        logger.debug(f"Loading sub page: {page_name} and sub_page: {sub_page}")
        logger.debug(f"{index.index.get(page)}")
        if index.index.get(page).get("sub_pages").get(sub_page) is None:
            logger.warning(f"Sub page {sub_page} not found in index")
            return render_template("404.html"), 404
        original_title = (
            index.index.get(page).get("sub_pages").get(sub_page).get("title")
        )
        md = index.index.get(page).get("md")
        if original_title != title:
            new_title = title
        else:
            new_title = None
        update_page = Page(original_title, md)
        update_page.update(content, original_title, new_title)
    else:
        if index.index.get(page) is None:
            logger.warning(f"Page {page} not found in index")
            return render_template("404.html"), 404
        title = index.index.get(page).get("title")
        update_page = Page(title)
        update_page.update(content, title)
    return (
        jsonify(
            {
                "message": f"Page {title} updated successfully",
                "url": update_page.url,
                "title": title,
                "md_file": update_page.md_file,
            }
        ),
        200,
    )


@bp.route("/<page>/<sub_page>/edit")
def edit_page(page: str, sub_page: str = None) -> str:
    """
    Renders the edit page
    """
    index_file = Path(os.environ.get("MD_PATH"), "current_pages.yaml")
    index = IndexHandling(index_file)
    index.load_index()
    memberdata = Memberdata()
    if sub_page:
        page_name = f"{page}/{sub_page}"
        logger.debug(f"Loading sub page: {page_name} and sub_page: {sub_page}")
        logger.debug(f"{index.index.get(page)}")
        if index.index.get(page).get("sub_pages").get(sub_page) is None:
            logger.warning(f"Sub page {sub_page} not found in index")
            return render_template("404.html"), 404
        title = index.index.get(page).get("sub_pages").get(sub_page).get("title")
        md = index.index.get(page).get("sub_pages").get(sub_page).get("md")
        page_content = Page(md)
    else:
        if index.index.get(page) is None:
            logger.warning(f"Page {page} not found in index")
            return render_template("404.html"), 404
        title = index.index.get(page).get("title")
        page_content = Page(index.index[page]["md"])
    logger.info(f"Loading page: {page_name if sub_page else page}")

    return render_template(
        "edit.html",
        title=title,
        page_content=page_content.render(),
        pages=index.index,
        memberdata=memberdata,
    )
