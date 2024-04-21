"""Module handling page add and remove from the database"""

from loguru import logger

from lfweb.database.connection import DbConnectionCredentials, GetDbConnection


class PagesDatabaseHandling:
    """Class for handling pages insertion and deletion in the databases pages and the index table"""

    def __init__(self):
        try:
            self.database_obj = DbConnectionCredentials()
        except Exception as e:
            logger.error(f"Error getting database credentials from env. vars: {e}")

    def add_page_to_index(self, title: str, url: str, md: str, sub_page: bool) -> bool:
        """Method adding a page to the index table"""
        with GetDbConnection(self.database_obj) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                            INSERT INTO pages (title, url, md) 
                            VALUES (%(title)s, %(url)s ,%(md)s)
                            """,
                    {"title": title, "url": url, "md": md},
                )
            conn.commit()

        return conn.close()
