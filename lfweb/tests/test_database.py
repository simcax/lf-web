"""Tests for database integration"""

import os

from psycopg import Connection

from lfweb.database.connection import GetDbConnection


def test_create_db_connection_credentials_from_env_vars(postgres_container, db_creds):
    """Test that we can create a database connection credentials object from env vars"""
    assert db_creds.host == os.getenv("DB_HOST")
    assert db_creds.port == os.getenv("DB_PORT")
    assert db_creds.username == os.getenv("DB_USERNAME")
    assert db_creds.password == os.getenv("DB_PASSWORD")
    assert db_creds.database == os.getenv("DB_NAME")


def test_pages_table_exists(postgres_container, init_db, db_creds):
    """Test that the pages table exists"""
    with GetDbConnection(db_creds) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM pages")
        rows = cur.fetchall()
        assert rows is not None


def test_connect_to_database(postgres_container, db_creds):
    """Test that we can connect to the database"""
    with GetDbConnection(db_creds) as connection:
        assert isinstance(connection, Connection)


# def test_add_a_page_to_the_database():
#     """Test that we can add a page to the database"""
#     db_creds = DbConnectionCredentials()
#     with GetDbConnection(db_creds) as cur:
#     page = {"title": "Test Page", "md": "test-page.md", "url": "/test-page"}
#     tempdir = TemporaryDirectory()
#     with tempdir as tmp:
#         page_path = os.path.join(tmp, page.get("md"))
#         with open(page_path, "w", encoding="utf-8") as file:
#             file.write("This is a test page.")
#             page_added = database.add_page(page)
#     assert page_added is True

# def test_add_page_to_database(postgres_container):
#     """Tests adding a page to the pages table by a method in the pages module"""
#     db = DatabaseMigration()
#     db.create_database()
#     with db.connection as conn:
#         db.run_migrations()
#         # Assuming there is a method in the pages module called "add_page"
#         # that adds a page to the pages table
#         pdh = PagesDatabaseHandling()
#         pdh.add_page_to_index(
#             "Test Page", "/testpage", "testpage.md", False
#         )  # TODO The MD field should be an id pointing to the id of the md table

#         # Check if the page was added successfully
#         pages_query = conn.execute(
#             text("SELECT * FROM pages WHERE title = 'Test Page'")
#         )
#         rows = pages_query.fetchall()
#         assert len(rows) == 1
