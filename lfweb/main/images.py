from flask import Blueprint, render_template, send_from_directory
from loguru import logger

bp = Blueprint("images", __name__, url_prefix="/static/images")


@bp.route("/logo.png")
def logo():
    """
    Returns the logo for the website
    """
    return send_from_directory(
        "static/images", "lejreFitnessLogoTransparentBg.png", mimetype="image/png"
    )
