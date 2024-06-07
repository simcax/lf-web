"""Module for handling the database connection"""

import os
from typing import Any

import psycopg
from loguru import logger
from pydantic import BaseModel, model_validator


class GetDbConnection:
    """Class for handling the database connection as a context manager"""

    host = ""
    port = ""
    username = ""
    password = ""
    database = ""
    connection = None

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


class DbConnectionCredentials(BaseModel):
    """Class for defining the database connection credentials"""

    host: str
    port: str
    username: str
    password: str
    database: str
    db_uri: str

    @model_validator(mode="after")
    @classmethod
    def set_credentials_from_env(cls, values: Any) -> Any:
        """Set the database connection credentials from the environment"""
        values.host = os.getenv("DB_HOST")
        values.port = os.getenv("DB_PORT")
        values.username = os.getenv("DB_USERNAME")
        values.password = os.getenv("DB_PASSWORD")
        values.database = os.getenv("DB_NAME")
        values.db_uri = os.getenv("DB_URI")
        return values
