import os
import sqlalchemy
from sqlalchemy.pool import NullPool
import pytest
from apollo_flask import create_app
import time

############ Configuration #######################
#We set these as environment variables so that they may be shared if needed.
os.environ['DATABASE_NAME'] = 'apollo_site.test'
os.environ['DATABASE_URI'] =  'postgresql://postgres@127.0.0.1/' + os.environ['DATABASE_NAME']
os.environ['DEFAULT_DATABASE_URI'] = 'postgresql://postgres@127.0.0.1/postgres'



from apollo_flask.db import init_db, session_scope, engine
from apollo_flask.db.models import *

#################################### Fixtures #################################
@pytest.fixture(scope="function")
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE_URI': os.environ['DATABASE_URI'],
        'DEFAULT_DATABASE_URI': os.environ['DEFAULT_DATABASE_URI'],
        'DATABASE_NAME': os.environ['DATABASE_NAME'],
    })
    with app.app_context():
        init_db()
    
    yield app

    #Dispose of engine (close all open DBAPI connections to the database)
    engine.dispose()
    print("Engine disposed")

@pytest.fixture
def client(app):
    return app.test_cleint()
    
@ pytest.fixture
def runner(app):
    return app.test_cli_runner()


