"""
Script for Heroku CLI. Usage:
    $ heroku run reinit_db
"""

from db_tools.debugging import reinit_db

if __name__ == '__main__':
    reinit_db()