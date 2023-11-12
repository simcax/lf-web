"""
Routes for images
"""
from flask import Blueprint, send_from_directory

bp = Blueprint("images", __name__, url_prefix="/static/images")


@bp.route("/logo.png")
def logo():
    """
    Returns the logo for the website
    """
    return send_from_directory(
        "static/images", "lejreFitnessLogoTransparentBg.png", mimetype="image/png"
    )
