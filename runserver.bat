@echo off
set DATABASE_URL=postgres://$(whoami)
set HEROKU_POSTGRESQL_ROSE_URL=postgres://$(whoami)
set FLASK_APP=webapp.py
set FLASK_DEBUG=1
set DEBUG_POSTGRES_PASSWORD=
flask run