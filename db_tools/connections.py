
"""
Exports a ContextManager Cursor for simple db access.
Also provides a CARDS_COL_HEADINGS list in case you need to merge db row 
results with they headings
"""

import os
import psycopg2
from psycopg2.extras import DictCursor
from urllib import parse as urlparse


basedir = os.path.abspath(os.path.dirname(__file__))
SCHEMA = os.path.join(basedir, 'schema.sql')

urlparse.uses_netloc.append("postgres")
URL = urlparse.urlparse(os.environ["DATABASE_URL"])


class Cursor():
    """Simple DictCursor context manager"""
    def __init__(self, query=None, cursor_factory=DictCursor):
        self.query = query
        self.factory = cursor_factory
        if not self._connect():
            print("failed to connect to db")


    def __enter__(self, *args):
        self.cursor = self.connection.cursor(cursor_factory=self.factory)
        query = self.query
        if query:
            self.cursor.execute(self.query)
        return self.cursor


    def __exit__(self, *args):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


    def _connect(self):
        try:
            conn = psycopg2.connect(
                database=URL.path[1:],
                user=URL.username,
                password=URL.password,
                host=URL.hostname,
                port=URL.port
            )
            self.connection = conn
            return conn
        except:
            self.connection = None
            return None
