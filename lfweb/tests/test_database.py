"""Tests for database integration"""

from psycopg import Connection

from lfweb.database.connection import Database


def test_create_database_object():
    """Test that we can create a database object"""
    db = Database()
    assert isinstance(db, Database) is True


def test_connect_to_database():
    """Test that we can connect to the database"""
    db = Database()
    assert isinstance(db.get_connection(), Connection)


def test_create_pages_table():
    """Test that we can create a pages table in the database"""
    db = Database()
    table_created = db.create_pages_table()
    assert table_created is True


def test_create_pages_table_already_created():
    """Test that we don't get an error if the table already exists"""
    db = Database()
    db.create_pages_table()
    table_created = db.create_pages_table()
    table_created_2 = db.create_pages_table()
    assert table_created_2 is True
