"""Module for handling the database connection"""

import os

import psycopg


class Database:
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
                    "CREATE TABLE pages (id SERIAL PRIMARY KEY, title VARCHAR(255), content TEXT)"
                )
                connection.commit()
            except psycopg.errors.DuplicateTable:
                pass
            finally:
                connection.close()
        return True


class GetDbConnection:
    """Class for handling the database connection as a context manager"""

    def __init__(self, create_database: bool = False) -> None:
        """Initialize the Database object"""
        self.host = os.environ.get("DB_HOST", "localhost")
        self.port = os.environ.get("DB_PORT", "5432")
        self.username = os.environ.get("DB_USERNAME", "lfweb")
        self.password = os.environ.get("DB_PASSWORD", "lfweb")
        self.database = os.environ.get("DB_DATABASE", "lfweb")
        if create_database:
            self._create_database(self.database, self._get_connection(no_db=True))

    def __enter__(self):
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

    def _create_database(self, database, connection):
        """Create a database in the postgresql server."""
        connection.autocommit = True
        cur = connection.cursor()
        try:
            cur.execute(f"CREATE DATABASE {database};")
        except psycopg.errors.DuplicateDatabase:
            pass
        finally:
            connection.close()
