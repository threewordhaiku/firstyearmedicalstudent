@echo off
setlocal enabledelayedexpansion
REM //////////////////////////////////////////////////////////////////////////

REM This script will start the Flask server on your computer (i.e. 'locally').
REM This should only be run within a pipenv shell.

REM For help on using this script, see the "Deploying Flask locally" comment 
REM on this Trello card:
REM     https://trello.com/c/rzDEieoG/70-heroku-app-deployment-steps

REM To run custom Flask commands:
REM     runflask.bat "python -m flask render"
REM This will run your command in the environment configured for Flask.
REM Note that you must wrap your Flask command in doublequotes (").

REM //////////////////////////////////////////////////////////////////////////


REM DATABASE_URL should not be left blank.
REM The app depends on the URL in this variable to connect to the database.
REM To connect to your local PostgreSQL database:
REM     DATABASE_URL=postgres://$(whoami)
REM To connect to Heroku database, follow steps on Trello as mentioned above.
REM You should end up with something like this:
REM     DATABASE_URL=postgres://<jumble>.compute-1.amazonaws.com:<jumble>
set DATABASE_URL=


REM If you are conneting to locally-stalled PostgreSQL database, place the 
REM password for your "postgres" user here (usually defined at installation). 
set DEBUG_POSTGRES_PASSWORD=


REM Settings for Flask
set FLASK_APP=webapp.py
set FLASK_DEBUG=1


REM Extract command from args
set command=%1


REM Execute Flask command or start the server
if defined command (
    %command:~1,-1%
) else (
    python webapp.py
)