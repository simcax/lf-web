"""
Configuration for pytest
"""

from os import environ

import pytest
from loguru import logger

from lfweb import create_app


@pytest.fixture
def redis_container():
    """
    Start a redis container
    """
    with RedisContainer("redis:7.0.12") as redis_container_cont:
        print(f"{redis_container_cont.get_container_host_ip()}")
        environ["REDIS_PORT"] = redis_container_cont.get_exposed_port("6379")
        environ["REDIS_HOST"] = redis_container_cont.get_container_host_ip()

        yield redis_container_cont


@pytest.fixture
def client():
    """Providess a client to test with"""
    logger.info("Starting test client")
    redis_port = environ.get("REDIS_PORT", "6379")
    redis_host = environ.get("REDIS_HOST", "localhost")
    logger.info(f"Redis host: {redis_host}")
    logger.info(f"Redis port: {redis_port}")
    app = create_app()

    # This will create a redics container on localhost
    # which is the default for the app factory settings
    with app.test_client() as app_client:
        with app.app_context():
            # None
            pass
        yield app_client
