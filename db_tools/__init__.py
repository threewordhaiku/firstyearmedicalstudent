"""
db_tools.py

Exports:
- Cursor: a context manager for simple db access.
- SCHEMA: absolute filepath to the database schema.sql
- URL:    a urlparse ParseResult for the DATABASE_URL from the app environment
"""

import os
import psycopg2
from psycopg2.extras import DictCursor
from urllib import parse


basedir = os.path.abspath(os.path.dirname(__file__))
SCHEMA = os.path.join(basedir, 'schema.sql')

parse.uses_netloc.append("postgres")
URL = parse.urlparse(os.environ["DATABASE_URL"])


class Cursor():
    """Simple DictCursor context manager.

    This class is preferably used as a context manager, such as:
        with Cursor() as c:
            c.execcute('query')

    To use this class without the `with` keyword:
        c = Cursor()
        cur = c.get_cursor()
        cur.execute('query')
        c.teardown_connection()

    Args:
        query: A string containing an SQL query to execute immediately when
               the database connection is opened and a cursor is created.
               Default: None
        
        cursor_factory: The factory class used in .get_cursor() when creating
                        db cursors. For more info, see: 
                            `http://initd.org/psycopg/docs/extras.html
                        Default: psycopg2.extras.DictCursor
    """
    def __init__(self, query=None, cursor_factory=DictCursor):
        self.query = query
        self.factory = cursor_factory

        # Connect to db
        self._connect()

        # Exec query
        cur = self.get_cursor()
        if query:
            cur.execute(query)
        return


    def get_cursor(self):
        """Creates a db cursor if one doesn't exist yet."""
        if not getattr(self, 'cursor', None):
            self.cursor = self.connection.cursor(cursor_factory=self.factory)
        return self.cursor


    def teardown_connection(self):
        """Commits queries and closes db connection."""
        if self.cursor:
            self.cursor.close()
        self.connection.commit()
        self.connection.close()


    def _connect(self):
        """Used to setup a connection to the database"""
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
            print("Failed to connect to %s" % URL)
            raise


    ### ContextManager magic methods
    def __enter__(self, *args):
        return self.get_cursor()

    def __exit__(self, *args):
        self.teardown_connection()