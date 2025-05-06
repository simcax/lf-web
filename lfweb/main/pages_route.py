"""Module for handling the pages automatically from config file"""

import os
import urllib
import urllib.parse

from flask import Blueprint, render_template, request
from loguru import logger

from lfweb.members.list import Memberdata
from lfweb.pages.index import IndexHandling
from lfweb.pages.page import Page

bp = Blueprint("route_pages", __name__, url_prefix="/pages")
bp_permalinks = Blueprint("route_permalinks", __name__, url_prefix="/permalinks")


def pages(page: str, sub_page: str = None) -> str:
    """
    Renders the pages
    """
    is_permalink = request.blueprint == "route_permalinks"
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
        title = sub_page_title
    else:
        if index.index.get(page) is None:
            logger.error(f"Page {page} not found in index")
            return render_template("404.html"), 404
        title = index.index.get(page).get("title")
        page_content = Page(title)
    logger.info(f"Loading page: {page_name if sub_page else page}")

    # the partials template:
    partial = render_template(
        "page.html",
        title=title,
        page_content=page_content.render(),
        pages=index.index,
        memberdata=memberdata,
    )

    if is_permalink:
        logger.info("Front page loading")
        index = IndexHandling()
        index.load_index()
        memberdata = Memberdata()
        version = os.environ.get("VERSION")
        google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

        return render_template(
            "home.html",
            pages=index.index,
            memberdata=memberdata,
            version=version,
            google_maps_api_key=google_maps_api_key,
            center_content=partial,
        )
    else:
        return partial


bp.add_url_rule(
    "/<page>",
    view_func=pages,
)
bp.add_url_rule(
    "/<page>/<sub_page>",
    view_func=pages,
)
bp_permalinks.add_url_rule(
    "/<page>",
    view_func=pages,
)
bp_permalinks.add_url_rule(
    "/<page>/<sub_page>",
    view_func=pages,
)


@bp.route("/create/<pagename>", methods=["POST"])
@bp.route("/create/<pagename>/<sub_page>", methods=["POST"])
def create_page(pagename: str, sub_page: str = None) -> str:
    """
    An endpoint which can take content to create a new page
    """
    content = request.form.get("content")
    title = request.form.get("title")
    is_sub_page = False
    if sub_page or bool(request.form.get("sub_page") == "true"):
        is_sub_page = True
        pagename = request.form.get("parent_page")
    if is_sub_page:
        index = IndexHandling()
        index.load_index()
        parent_md_page_name = index.index.get(pagename).get("md")
        logger.debug(f"Creating sub page: {pagename}")
    else:
        parent_md_page_name = None
    page = Page(title, parent_md_page_name)
    page.create(content)
    return render_template(
        "snippets/page_created.html",
        title=title,
        url=page.url,
        message=f"Page {title} created successfully",
    )


@bp.route("/update/<page>", methods=["POST"])
@bp.route("/update/<page>/<sub_page>", methods=["POST"])
def update_page_content(page: str, sub_page: str = None) -> str:
    """Updates page content, and stores it in the md file"""

    index = IndexHandling()
    page_title = request.values.get("title")
    content = request.form.get("content")
    index.load_index()
    if sub_page:
        page_name = f"{page}/{sub_page}"
        logger.debug(f"Loading sub page: {page_name} and sub_page: {sub_page}")
        logger.debug(f"{index.index.get(page)}")
        if index.index.get(page).get("sub_pages").get(sub_page) is None:
            logger.error(f"Sub page {sub_page} not found in index")
            return render_template("404.html"), 404
        original_title = (
            index.index.get(page).get("sub_pages").get(sub_page).get("title")
        )
        md = index.index.get(page).get("md")
        if original_title != page_title:
            new_title = page_title
        else:
            new_title = None
        update_page = Page(original_title, md)
        update_page.update(content, original_title, new_title)
    else:
        if index.index.get(page) is None:
            logger.warning(f"Page {page} not found in index")
            return render_template("404.html"), 404
        original_title = index.index.get(page).get("title")
        if original_title != page_title:
            new_title = page_title
        else:
            new_title = None
        update_page = Page(original_title)
        update_page.update(content, original_title, new_title)
    reload_url = (
        request.referrer.replace(
            f"page_name={page}", f"page_name={update_page.index_title}"
        ).replace(
            f"title={urllib.parse.quote(original_title)}",
            f"title={urllib.parse.quote(new_title)}",
        )
        if new_title
        else False
    )
    return render_template(
        "snippets/editor_result.html",
        title=page_title,
        url=update_page.url,
        message=f"Page {page_title} updated successfully",
        reload_url=reload_url,
    )


@bp.route("/<page>/<sub_page>/edit", methods=["GET", "POST"])
def edit_page(page: str, sub_page: str = None) -> str:
    """
    Renders the edit page
    """
    index = IndexHandling()
    index.load_index()
    memberdata = Memberdata()
    if sub_page:
        page_name = f"{page}/{sub_page}"
        logger.debug(f"Loading sub page: {page_name} and sub_page: {sub_page}")
        logger.debug(f"{index.index.get(page)}")
        if index.index.get(page).get("sub_pages").get(sub_page) is None:
            logger.error(f"Sub page {sub_page} not found in index")
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


@bp.route("/delete/<page>", methods=["POST"])
@bp.route("/delete/<page>/<sub_page>", methods=["POST"])
def delete_page(page: str, sub_page: str = None) -> str:
    """Deletes a page and its content"""
    if sub_page:
        page = Page(sub_page, page)
        title = page.title
        logger.debug(f"Deleting sub page: {page}")
        page.delete()
    else:
        page = Page(page)
        title = page.title
        logger.debug(f"Deleting page: {page}")
        page.delete()

    return render_template(
        "snippets/page_deleted.html",
        title=title,
    )
