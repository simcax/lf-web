"""Test for setting up the database migrations"""

import sqlalchemy
from sqlalchemy import text

from lfweb.database.db_migration import DatabaseMigration
from lfweb.pages.database import PagesDatabaseHandling


def test_create_database_migration_object():
    """Test that we can create a database migration object"""
    db = DatabaseMigration()
    assert isinstance(db, DatabaseMigration) is True


def test_create_database_migration_object_with_args(postgres_container):
    """Test that we can create a database migration object with args"""
    db = DatabaseMigration()
    assert isinstance(db, DatabaseMigration) is True


def test_database_being_created(postgres_container):
    """Test that we can create the database"""
    db = DatabaseMigration()
    db.create_database()
    with db.connection as conn:
        databases_query = conn.execute(text("SELECT datname FROM pg_database"))
        rows = databases_query.fetchall()
        databases = [row[0] for row in rows]
        assert postgres_container.POSTGRES_DB in databases


def test_create_tables(postgres_container):
    """Test that we can create the tables"""
    db = DatabaseMigration()
    db.create_database()
    with db.connection as conn:
        db.run_migrations()
        tables_query = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        rows = tables_query.fetchall()
        tables = [row[0] for row in rows]
        assert "pages" in tables


def test_drop_tables(postgres_container):
    """Tests dropping the tables from the database"""
    db = DatabaseMigration()
    db.create_database()
    with db.connection as conn:
        db.run_migrations()
        db.drop_tables()
        tables_query = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        rows = tables_query.fetchall()
        tables = [row[0] for row in rows]
        assert "pages" not in tables
        assert "index" not in tables
        assert "md" not in tables
