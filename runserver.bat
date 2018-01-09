@echo off
REM //////////////////////////////////////////////////////////////////////////

REM This script will start the Flask server on your computer (i.e. 'locally').
REM This should only be run within a pipenv shell.

REM For help on using this script, see the "Deploying Flask locally" section 
REM on this Trello card:
REM   https://trello.com/c/rzDEieoG/70-heroku-app-deployment-steps

REM //////////////////////////////////////////////////////////////////////////


REM Using the Heroku-recommended env var for URLs. The app will load custom
REM connection info when it encounters this value in DATABASE_URL.
set DATABASE_URL=postgres://$(whoami)

REM Place the password to your "postgres" user here (usually defined during
REM installation). This variable should not be left blank.
set DEBUG_POSTGRES_PASSWORD=

REM Settings for Flask
set FLASK_APP=webapp.py
set FLASK_DEBUG=1

REM Start the server
flask run