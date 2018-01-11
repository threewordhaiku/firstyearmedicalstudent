"""
module db_tools

Exports:
  Classes:
    - AppDBConnection: database connection to the app database
    - AppCursor: context manager for executing simple queries
  Vars:
    - SCHEMA: absolute filepath to the database schema.sql
    - POSTGRES_ENVVAR: The name of the environment variable defining the 
                       PostgreSQL database URL the app will connect to.
                       For if we ever need multiple databases.
    - DB_PARSED_URL: a urlparse ParseResult for the PostgreSQL database URL
    - DB_URL = The raw, unparsed URL to the PostgreSQL database
"""

import os
import psycopg2
from psycopg2.extras import DictCursor
from urllib import parse


# Setup for creating exported vars
basedir = os.path.abspath(os.path.dirname(__file__))
parse.uses_netloc.append("postgres")

# Absolute link to db schema
SCHEMA = os.path.join(basedir, 'schema.sql')

# Name of the env var on Heroku containing the URL to the PostgreSQL db
POSTGRES_ENVVAR = 'DATABASE_URL'

# Retrieve URL in the env var
DB_URL = os.environ[POSTGRES_ENVVAR]

# Create localhost URI if DB_URL uses $(whoami) to imply locally hosted db
if DB_URL == r'postgres://$(whoami)':
    _DEBUG_PW = os.environ.get('DEBUG_POSTGRES_PASSWORD', None)
    if not _DEBUG_PW:
        raise Exception("Password for local database user 'postgres' not "
                        "defined. Please set your password in the "
                        "environment variable 'DEBUG_POSTGRES_PASSWORD'.")
    DB_URL = 'postgres://postgres:{}@localhost:5432'.format(_DEBUG_PW)

# Parse URI into a ParseResult
DB_PARSED_URL = parse.urlparse(DB_URL)
print("Using database at {}".format(DB_PARSED_URL.hostname))


class AppDBConnection():
    """Simple class that provides a connection to the app db.

    AppDBConnections are threadsafe, but their cursors are not. If you're not 
    sure how cursors work, use the AppCursor instead.

    Usage: 
        conn = AppDBConnection()
        cur = conn.cursor
        cur.execute('query1')
        cur.execute('query2')
        conn.teardown()
    """
    def __init__(self):
        self.cursors = []
        # Connect to db
        self._connect()


    @property
    def cursor(self, factory=DictCursor):
        """Provides a fresh db cursor.

        Args:
            factory: a psycopg2 extension cursor. See:
                     http://initd.org/psycopg/docs/AppDBConnection.html#AppDBConnection.cursor
                     Default: psycopg2.extras.DictCursor

        """
        return self._conn.cursor(cursor_factory=factory)


    def teardown(self):
        """Commits queries and closes the db connection."""
        for cur in self.cursors:
            cur.close()
        self._conn.commit()
        self._conn.close()


    def _connect(self):
        """Setup the connection to the database."""
        try:
            conn = psycopg2.connect(
                database=DB_PARSED_URL.path[1:],
                user=DB_PARSED_URL.username,
                password=DB_PARSED_URL.password,
                host=DB_PARSED_URL.hostname,
                port=DB_PARSED_URL.port
            )
            self._conn = conn
            return self._conn
        except:
            print("Failed to connect to database at", DB_PARSED_URL.hostname)
            raise



class AppCursor(AppDBConnection):
    """Context manager for executing simple queries

    Usage:
        with AppCursor as cur:
            cur.execute('query1')
            cur.execute('query1')
    """
    def __init__(self, *args, **kwargs):
        super(AppCursor, self).__init__(*args, **kwargs)

     ### ContextManager magic methods
    def __enter__(self, *args):
        return self.cursor

    def __exit__(self, *args):
        self.teardown()