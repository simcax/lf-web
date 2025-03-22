"""Lejre Fitness Website - Flask App"""

from os import environ, urandom

import redis
import sentry_sdk
from flask import Flask  # , render_template, send_from_directory, session
from flask_session import Session
from loguru import logger
from werkzeug.http import dump_cookie

from lfweb.main import (  # pylint: disable=import-outside-toplevel
    frontpage_bp,
    images_bp,
    pages_bp,
)

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
