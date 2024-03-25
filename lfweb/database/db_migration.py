import os

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy_utils import create_database, database_exists


class DatabaseMigration:
    """Class for handling the postgresql database migration"""

    def __init__(self) -> None:
        """Initialize the Database object with a database connection"""
        try:
            self.engine = create_engine(os.getenv("DB_URI"), echo=True)
        except Exception as e:
            print(f"Error creating engine: {e}")
        else:
            self.connection = self.engine.connect()

    def create_database(self):
        """Create the database"""
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    def run_migrations(self):
        """Run the database migrations"""
        try:
            self.create_table_pages()
        # self.create_table_index()
        except Exception as e:
            print(f"Error running migrations: {e}")
        else:
            print("Migrations ran successfully")

    def create_table_pages(self):
        """Create the pages table"""
        metadata = MetaData()
        pages = Table(
            "pages",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("title", String),
            Column("md", Text),
            Column("url", String),
            Column("sub_page", Boolean, default=False),
        )
        index = Table(
            "index",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("pages_id", ForeignKey("pages.id")),
        )
        metadata.create_all(self.engine)
        self.connection.commit()

    def create_table_index(self):
        """Create the index table"""
        metadata = MetaData()
        index = Table(
            "index",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("pages_id", ForeignKey("pages.id")),
        )
        metadata.create_all(self.engine)
