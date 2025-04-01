"""
Configuration for pytest
"""

import random
import string
from os import environ

import pytest
from dotenv import load_dotenv
from loguru import logger
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from lfweb import create_app
from lfweb.database.connection import DbConnectionCredentials
from lfweb.database.db_migration import DatabaseMigration

load_dotenv()


@pytest.fixture(scope="package")
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

    yield postgres

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)


@pytest.fixture
def init_db():
    """
    Initialize the database
    """
    db = DatabaseMigration()
    db.create_database()
    with db.connection as conn:  # noqa F841
        db.run_migrations()
    yield db
    db.drop_tables()


@pytest.fixture
def db_creds():
    """Fixture for database credentials"""
    db_creds = DbConnectionCredentials(
        host=environ.get("DB_HOST"),
        port=environ.get("DB_PORT"),
        username=environ.get("DB_USERNAME"),
        password=environ.get("DB_PASSWORD"),
        database=environ.get("DB_NAME"),
        db_uri=environ.get("DB_URI"),
    )
    return db_creds


@pytest.fixture
def doorcount_html():
    """Fixture for doorcount HTML"""
    return """
    <html>
<head>
	<title>Antal medlemmer i bygning</title>
	<meta http-equiv="refresh" content="300">
</head>
<body>
	<b>Ankommet for tid siden:</b><br/>90 minutter: 1<br/>75 minutter: 3<br/>60 minutter: 3<br/>45 minutter: 3<br/>30 minutter: 0<br/>15 minutter: 2<br/><br/><i>Senest opdateret: 24. marts 2025, kl. 11:06</i>
</body>
</html>"""


@pytest.fixture
def random_id(size=6, chars=string.ascii_uppercase + string.digits):
    """Fixture for generating a random ID"""
    return "".join(random.choice(chars) for _ in range(size))
