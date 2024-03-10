"""Lejre Fitness Website - Flask App"""

from os import environ, urandom

import redis
from flask import Flask  # , render_template, send_from_directory, session
from flask_session import Session
from loguru import logger

from lfweb.main import (  # pylint: disable=import-outside-toplevel
    frontpage_bp,
    images_bp,
    pages_bp,
)

# from .routes import ()


def create_app(test_config=None):
    # Disabling no-member, since app.logger comes from the flask framework
    # pylint: disable=no-member
    """App factory"""
    site_short_name = "lf-web"
    secret_key = str(urandom(12).hex())
    app = Flask(__name__, instance_relative_config=True)
    redis_host = environ.get("REDIS_HOST", "localhost")
    redis_port = environ.get("REDIS_PORT", "6379")
    logger.info("Redis host: %", redis_host)
    logger.info("Redis port: %", redis_port)
    app.config.from_mapping(
        SECRET_KEY=environ.get("SECRET_KEY", secret_key),
        SESSION_TYPE="redis",
        SESSION_REDIS=redis.from_url(f"redis://{redis_host}:{redis_port}"),
        SESSION_PERMANENT=True,
        SESSION_USE_SIGNER=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_DOMAIN=environ.get("SESSION_COOKIE_DOMAIN", str("127.0.0.1")),
        SESSION_COOKIE_NAME=environ.get("SESSION_COOKIE_NAME", site_short_name),
    )
    print(secret_key)
    if test_config:
        app.logger.info("Test config is set")
    logger.info(app.config)
    sess = Session()
    print(f"sess = {sess}")
    with app.app_context():
        sess.init_app(app)
        # app.register_blueprint(some_route.bp1)

        app.register_blueprint(frontpage_bp)
        app.register_blueprint(images_bp)
        app.register_blueprint(pages_bp)

        app.logger.info("App routes loaded")
        app.logger.info(app.url_map)
        return app
