"""Module for handling the database connection"""

import os

import psycopg


class Database:
    """Class for handling the postgresql database connection"""

    def __init__(self):
        """Initialize the Database object"""
        pass

    def get_connection(self):
        """Connect to the database"""
        host = os.environ.get("DB_HOST", "localhost")
        port = os.environ.get("DB_PORT", "5432")
        username = os.environ.get("DB_USERNAME", "lfweb")
        password = os.environ.get("DB_PASSWORD", "lfweb")
        database = os.environ.get("DB_DATABASE", "lfweb")
        connection = psycopg.connect(
            f"host={host} user={username} password={password} port={port}"
        )
        connection.autocommit = True
        cur = connection.cursor()
        try:
            cur.execute(f"CREATE DATABASE {database};")
        except psycopg.errors.DuplicateDatabase:
            pass
        finally:
            connection.close()
        return psycopg.connect(
            f"host={host} user={username} password={password} port={port} dbname={database}"
        )

    def create_pages_table(self):
        """Create a pages table in the database"""
        with self.get_connection() as connection:
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
