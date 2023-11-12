from flask import Blueprint
from loguru import logger

bp = Blueprint("pages", __name__, url_prefix="/")

from lfweb.main import routes
