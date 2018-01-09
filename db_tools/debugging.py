"""
Contains debugging functions:
    - exec_file(): Executes an SQL file into the app DB
    - reinit_db(): Re-initializes the database with sample table data
"""

import os.path
from . import Cursor

def exec_file(abs_filepath):
    with open(abs_filepath) as f:
        content = f.read()
    with Cursor() as cur:
        cur.execute(content)


def reinit_db():
    basedir = os.path.abspath(os.path.dirname(__file__))
    for fname in ['schema.sql', 'sample.sql']:
        abspath = os.path.join(basedir, fname)
        exec_file(abspath)