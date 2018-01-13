"""
Contains debugging functions:
    - exec_file_to_db(): 
        executes an SQL file into the app DB
    - init_db(): 
        (re-)initializes the database with sample table data
    - load_sample():
        inserts sample data into database
"""

import os.path
from . import AppCursor

basedir = os.path.abspath(os.path.dirname(__file__))

def exec_file_to_db(abs_filepath):
    with open(abs_filepath) as f:
        content = f.read()
    with AppCursor() as cur:
        cur.execute(content)


def init_db():
    abspath = os.path.join(basedir, 'schema.sql')
    exec_file_to_db(abspath)

def load_sample():
    abspath = os.path.join(basedir, 'sample.sql')
    exec_file_to_db(abspath)
