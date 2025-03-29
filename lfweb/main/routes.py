"""
Routes for core pages
"""

import os

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
    index = IndexHandling("lfweb/pages/current_pages.yaml")
    index.load_index()
    memberdata = Memberdata()

    return render_template("home.html", pages=index.index, memberdata=memberdata)


@frontpage_bp.route("/memberships")
def memberships():
    """
    Renders the memberships page
    """
    memberdata = Memberdata()
    return render_template("snippets/membership_test.html", memberdata=memberdata)


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
