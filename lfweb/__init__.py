"""Lejre Fitness Website - Flask App"""

import os
from datetime import datetime, timedelta
from os import environ, urandom

import redis
import sentry_sdk
from flask import Flask, session  # , render_template, send_from_directory, session
from flask_session import Session
from loguru import logger
from werkzeug.http import dump_cookie

from lfweb.main import (  # pylint: disable=import-outside-toplevel
    auth,
    editor_bp,
    frontpage_bp,
    images_bp,
    pages_bp,
    permalinks_bp,
)

basedir = os.path.abspath(os.path.dirname(__file__))

app_environment = environ.get("ENVIRONMENT_NAME", "development")
version = environ.get("VERSION")

# from .routes import ()
sentry_sdk.init(
    dsn="https://f90b2619be9af44f465a5b48a7135f31@o4505902934130688.ingest.us.sentry.io/4505902934261760",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    send_default_pii=True,
    environment=app_environment,
    release=version,
)


def create_app(test_config=None):
    # Disabling no-member, since app.logger comes from the flask framework
    # pylint: disable=no-member
    """App factory"""

    site_short_name = "lf-web"
    secret_key = str(urandom(12).hex())
    app = Flask(__name__, instance_relative_config=True)
    redis_host = environ.get("REDIS_HOST", "localhost")
    redis_port = environ.get("REDIS_PORT", "6379")
    logger.info(f"Redis host: {redis_host}")
    logger.info(f"Redis port: {redis_port}")
    app.config.from_mapping(
        SECRET_KEY=environ.get("SECRET_KEY", secret_key),
        SESSION_TYPE="redis",
        SESSION_REDIS=redis.from_url(f"redis://{redis_host}:{redis_port}"),
        SESSION_PERMANENT=True,
        SESSION_USE_SIGNER=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_DOMAIN=str(environ.get("SESSION_COOKIE_DOMAIN", "127.0.0.1")),
        SESSION_COOKIE_NAME=str(environ.get("SESSION_COOKIE_NAME", site_short_name)),
        SESSION_COOKIE_HTTPONLY=True,  # Prevents JavaScript access to cookies
        PERMANENT_SESSION_LIFETIME=timedelta(days=14),  # Controls session expiration
        MAX_CONTENT_LENGTH=1024 * 1024 * 16,  # 16 MB
    )
    app.config["MDEDITOR_FILE_UPLOADER"] = os.path.join(
        basedir, "uploads"
    )  # this floder uesd to save your uploaded image

    print(secret_key)
    if test_config:
        app.logger.info("Test config is set")
    logger.info(app.config)
    sess = Session()
    print(f"sess = {sess}")
    with app.app_context():
        sess.init_app(app)
        # app.register_blueprint(some_route.bp1)

        app.register_blueprint(editor_bp)
        app.register_blueprint(frontpage_bp)
        app.register_blueprint(images_bp)
        app.register_blueprint(pages_bp)
        app.register_blueprint(permalinks_bp)
        app.register_blueprint(auth.bp)

        app.logger.info("App routes loaded")
        app.logger.info(app.url_map)
        return app

    # Let's make sessions permanent, if site is visited every 5 days
    @app.before_request
    def make_session_permanent():
        """
        Make the session stick for at least 5 days.
        """
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(days=5)
