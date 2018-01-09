"""
db_tools.py

Exports:
  Classes:
    - Cursor: a context manager for simple db access.
  Vars:
    - SCHEMA: absolute filepath to the database schema.sql
    - POSTGRES_ENVVAR: The name of the environment variable defining the 
                       PostgreSQL database URL the app will connect to.
    - DB_PARSED_URL: a urlparse ParseResult for the PostgreSQL database URL
    - DB_URL = The raw, unparsed URL to the PostgreSQL database
"""

import os
import psycopg2
from psycopg2.extras import DictCursor
from urllib import parse

#from .debugging import get_debug_connection

# Setup for creating exported vars
basedir = os.path.abspath(os.path.dirname(__file__))
parse.uses_netloc.append("postgres")

# Absolute link to db schema
SCHEMA = os.path.join(basedir, 'schema.sql')

# Name of the env var on Heroku containing the URL to the PostgreSQL db
POSTGRES_ENVVAR = 'DATABASE_URL' # Production DB

# Retrieve and parse the URL in the env var
DB_URL = os.environ[POSTGRES_ENVVAR]
if DB_URL == r'postgres://$(whoami)':
    debug_pw = os.environ.get('DEBUG_POSTGRES_PASSWORD', None)
    if not debug_pw:
        raise Exception("Password for local database connection not "
                        "defined. Please set your password in the "
                        "environment variable 'DEBUG_POSTGRES_PASSWORD'.")
    DB_URL = 'postgres://postgres:{}@localhost:5432'.format(debug_pw)
DB_PARSED_URL = parse.urlparse(DB_URL)
print("Connecting to database at {}".format(DB_URL))


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
                database=DB_PARSED_URL.path[1:],
                user=DB_PARSED_URL.username,
                password=DB_PARSED_URL.password,
                host=DB_PARSED_URL.hostname,
                port=DB_PARSED_URL.port
            )
            self.connection = conn
            return conn
        except:
            print("Failed to connect to %s" % DB_URL)
            raise

    def _debug_connect(self):
        """Workaround to login to locally-hosted db

        psycopg2 seems to have trouble parsing the URL provided by Heroku docs
        (i.e. 'postgres://$(whoami)'). This function manually supplies 
        connection info.
        When running this app locally, you have to define 
        """
        conn = psycopg2.connect(
            database='postgres',
            user=r'postgres',
            password=debug_pw,
            host=r'localhost',
            port=5432
        )
        self.connection = conn
        return conn


    ### ContextManager magic methods
    def __enter__(self, *args):
        return self.get_cursor()

    def __exit__(self, *args):
        self.teardown_connection()