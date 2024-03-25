"""Module for handling the database connection"""

import os
from pathlib import Path

import psycopg
from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists


class OldDatabase:
    """Class for handling the postgresql database connection"""

    def __init__(self, create_database: bool = False) -> None:
        """Initialize the Database object"""
        self.init_create_database = create_database

    def create_pages_table(self):
        """Create a pages table in the database"""

        with GetDbConnection(self.init_create_database) as connection:
            cur = connection.cursor()
            try:
                cur.execute(
                    "CREATE TABLE pages (id SERIAL PRIMARY KEY, title VARCHAR(255), content TEXT, md VARCHAR(255), url VARCHAR(255))"
                )
                connection.commit()
            except psycopg.errors.DuplicateTable:
                pass
            finally:
                connection.close()
        return True

    def create_index_table(self):
        """Create an index table in the database"""

        with GetDbConnection(self.init_create_database) as connection:
            cur = connection.cursor()
            try:
                cur.execute(
                    "CREATE TABLE index (id SERIAL PRIMARY KEY, title VARCHAR(255), url VARCHAR(255), md VARCHAR(255), content TEXT)"
                )
                connection.commit()
            except psycopg.errors.DuplicateTable:
                pass
            finally:
                connection.close()
        return True

    def add_page(self, page):
        """Add a page to the database"""

        with GetDbConnection() as connection:
            cur = connection.cursor()
            try:
                cur.execute(
                    "INSERT INTO pages (title, content, md) VALUES (%s, %s, %s)",
                    (
                        page.get("title"),
                        page.get("content"),
                        page.get("md"),
                    ),
                )
                connection.commit()
            except psycopg.errors.UniqueViolation:
                return False
            finally:
                connection.close()
        return True


class GetDbConnection:
    """Class for handling the database connection as a context manager"""

    def __init__(self, database_obj) -> None:
        """Initialize the Database object"""
        self.host = database_obj.host
        self.port = database_obj.port
        self.username = database_obj.username
        self.password = database_obj.password
        self.database = database_obj.database

    def __enter__(self):
        logger.info(f"Connecting to database {self.database}")
        self.connection = self._get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def _get_connection(self, no_db=False):
        """Get a connection to the database"""
        return psycopg.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            dbname=self.database if not no_db else None,
        )


class Database:
    """Class for handling the postgresql database connection"""

    def __init__(self, database: str = None) -> None:
        """Initialize the Database object"""
        self.host = os.environ.get("DB_HOST", "localhost")
        self.port = os.environ.get("DB_PORT", "5432")
        self.username = os.environ.get("DB_USERNAME", "lfweb")
        self.password = os.environ.get("DB_PASSWORD", "lfweb")
        self.database = database if database else os.environ.get("DB_DATABASE", "lfweb")
        self.db_uri = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(self.db_uri)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    def migration(self):
        """Run the database migrations"""
        os.environ["DB_URI"] = self.db_uri
        current_dir = Path(__file__).parent
        alembic_ini_exists = (current_dir / "../../alembic.ini").exists()
        alembic_cfg = Config(current_dir / "../../alembic.ini")
        command.revision(alembic_cfg, autogenerate=True)
        command.upgrade(alembic_cfg, "head")
