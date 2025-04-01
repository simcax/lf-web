"""
Routes for core pages
"""

import os
from pathlib import Path

from flask import Blueprint, render_template
from loguru import logger

from lfweb.members.list import Memberdata
from lfweb.pages.index import IndexHandling
from lfweb.utils.doorcount_scrape import DoorCountScraper

frontpage_bp = Blueprint("main", __name__, url_prefix="/", template_folder="templates")


@frontpage_bp.route("/")
def frontpage():
    """
    Renders the frontpage
    """
    logger.info("Front page loading")
    index_path = Path(os.environ.get("MD_PATH"), "current_pages.yaml")
    index = IndexHandling(index_path)
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
    )


@frontpage_bp.route("/memberships")
def memberships():
    """
    Renders the memberships page
    """
    memberdata = Memberdata()
    activity_list_url = os.environ.get("ACTIVITY_LIST_URL")
    if activity_list_url is None:
        logger.warning("ACTIVITY_LIST_URL not set in environment variables")
    return render_template(
        "snippets/membership.html",
        memberdata=memberdata,
        activity_list_url=activity_list_url,
    )


@frontpage_bp.route("/doorcount")
def doorcount():
    """
    Renders the doorcount page
    """
    url = os.environ.get("DOORCOUNT_URL")
    scraper = DoorCountScraper(url)
    page = scraper.fetch_page()
    data = scraper.parse_data(page)
    return render_template("snippets/doorcount.html", data=data)


@frontpage_bp.route("/membercount")
def membercount():
    """
    Renders the membercount page
    """
    memberdata = Memberdata()
    return render_template("snippets/membercount.html", memberdata=memberdata)
