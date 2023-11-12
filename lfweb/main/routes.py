"""
Routes for core pages
"""
from flask import render_template
from loguru import logger

from lfweb.main import bp


@bp.route("/")
def frontpage():
    """
    Renders the frontpage
    """
    logger.info("Front page loading")
    return render_template("home.html")
