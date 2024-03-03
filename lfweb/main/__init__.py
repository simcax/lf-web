"""
Main routes for the application
"""

from flask import Blueprint
from loguru import logger

from .images import bp as images_bp
from .pages_route import bp as pages_bp
from .routes import frontpage_bp

# bp = Blueprint("pages", __name__, url_prefix="/")

# from lfweb.main import routes  # pylint: disable=wrong-import-position


# bp = Blueprint("pages", __name__, url_prefix="/")
