"""Tests for database integration"""

import os
from tempfile import TemporaryDirectory

from psycopg import Connection

from lfweb.database.connection import Database, GetDbConnection


def test_create_database_object():
    """Test that we can create a database object"""
    db = Database()
    assert isinstance(db, Database) is True


def test_pages_table_exists():
    """Test that the pages table exists"""
    db = Database("ourtestdb")
    db.migration()
    with GetDbConnection(db) as connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM pages")
        rows = cur.fetchall()
        assert rows is not None


def test_connect_to_database():
    """Test that we can connect to the database"""
    with GetDbConnection(True) as connection:
        assert isinstance(connection, Connection)


def test_create_pages_table():
    """Test that we can create a pages table in the database"""
    database = Database(True)
    table_created = database.create_pages_table()
    assert table_created is True


def test_create_pages_table_already_created():
    """Test that we don't get an error if the table already exists"""
    database = Database(False)
    table_created = database.create_pages_table()
    table_created_2 = database.create_pages_table()
    assert table_created_2 is True


def test_create_index_table():
    """Test that we can create an index table in the database"""
    database = Database(True)
    table_created = database.create_index_table()
    assert table_created is True


def test_add_a_page_to_the_database():
    """Test that we can add a page to the database"""
    database = Database(True)
    page = {"title": "Test Page", "md": "test-page.md", "url": "/test-page"}
    tempdir = TemporaryDirectory()
    with tempdir as tmp:
        page_path = os.path.join(tmp, page.get("md"))
        with open(page_path, "w", encoding="utf-8") as file:
            file.write("This is a test page.")
            page_added = database.add_page(page)
    assert page_added is True
