"""
Main routes for the application
"""

from flask import Blueprint  # noqa: F401
from loguru import logger  # noqa: F401

from .auth import bp as auth_bp  # noqa: F401
from .editor_routes import bp as editor_bp  # noqa: F401
from .images import bp as images_bp  # noqa: F401
from .pages_route import bp as pages_bp  # noqa: F401
from .pages_route import bp_permalinks as permalinks_bp  # noqa: F401
from .routes import frontpage_bp  # noqa: F401
