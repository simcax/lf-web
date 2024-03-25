"""
Configuration for pytest
"""

from os import environ

import pytest
from loguru import logger
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from lfweb import create_app
from lfweb.database.connection import Database, GetDbConnection


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


@pytest.fixture(scope="package")
def client(redis_container):
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


@pytest.fixture(scope="package", autouse=True)
def postgres_container(request):
    """
    Start a postgres container
    """
    postgres = PostgresContainer("postgres:16-alpine")
    postgres.start()
    logger.info(f"Postgres container started at {postgres.get_container_host_ip()}")
    environ["DB_CONN"] = postgres.get_connection_url()
    environ["DB_HOST"] = postgres.get_container_host_ip()
    environ["DB_PORT"] = postgres.get_exposed_port(5432)
    environ["DB_USERNAME"] = postgres.POSTGRES_USER
    environ["DB_PASSWORD"] = postgres.POSTGRES_PASSWORD
    environ["DB_NAME"] = postgres.POSTGRES_DB
    environ["DB_URI"] = postgres.get_connection_url()
    db_engine = Database()

    yield db_engine

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)
