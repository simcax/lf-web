"""
Main routes for the application
"""

from flask import Blueprint
from loguru import logger

from .images import bp as images_bp
from .pages_route import bp as pages_bp
from .routes import frontpage_bp
