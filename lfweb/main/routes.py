"""
Routes for core pages
"""

from flask import Blueprint, render_template
from loguru import logger

from lfweb.members.list import Memberdata
from lfweb.pages.index import IndexHandling

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
