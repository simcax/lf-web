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


@bp.route("/yoga.jpg")
def yoga_image():
    """
    Returns the image for the yoga carousel
    """
    return send_from_directory(
        "static/images",
        "ginny-rose-stewart-UxkcSzRWM2s-unsplash.jpg",
        mimetype="image/jpg",
    )


@bp.route("/circletraining.jpg")
def circletraining_image():
    """
    Returns the image for the yoga carousel
    """
    return send_from_directory(
        "static/images",
        "colin-czerwinski-hUsRfp5VumA-unsplash.jpg",
        mimetype="image/jpg",
    )


@bp.route("/<path:filename>")
def image(filename):
    """
    Returns the image for the yoga carousel
    """
    return send_from_directory(
        "static/images",
        filename,
        mimetype="image/jpg",
    )
