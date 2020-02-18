### Add the instance folder to the path. We modify the variables 
# declared in instance/config.py to set up the testing databases.
import sys
sys.path.append('../instance')
from config import *

import os
import sqlalchemy
from sqlalchemy.pool import NullPool
import pytest
from apollo_flask import create_app
from apollo_flask.db.models.garmin_oauth import User_Id
import time
import secrets

############ Configuration #######################

from apollo_flask.db import init_db
from apollo_flask.db.models import *

#################################### Fixtures #################################
@pytest.fixture(scope="function")
def app():
    #Create a suffix for the database so that each test runs in its own db
    db_suffix_name = os.environ['PYTEST_CURRENT_TEST'].split(':')[-1].split(' ')[0]
    db_suffix_random = '_' + secrets.token_urlsafe(16)

    
    app = create_app({
        'TESTING': True,
        'DATABASE_URI': DATABASE_URI + ':' + db_suffix_name + db_suffix_random,
        'DATABASE_NAME' : DATABASE_NAME + ':' + db_suffix_name + db_suffix_random,
        'DEFAULT_DATABASE_URI' : DEFAULT_DATABASE_URI
    })
    with app.app_context():
        init_db()
    
    yield app

    #Dispose of engine (close all open DBAPI connections to the database)
    app.config['ENGINE'].dispose()
    print("Engine disposed")
    
    #Delete the testing database
    _engine = sqlalchemy.create_engine(DEFAULT_DATABASE_URI)
    # Grab the underlying connection; databases can't be created inside of
    # regular transactions
    _conn = _engine.connect()
    # Close the "connection" transaction
    _conn.execute('commit')

    # Drop the database 
    _conn.execute('DROP DATABASE "' + database_name + '"')
    print("INFO: Database dropped.")
    _conn.execute('commit')



@pytest.fixture
def client(app):
    return app.test_client()
    
@ pytest.fixture
def runner(app):
    return app.test_cli_runner()


def add_uids(json_data, session_scope):
    """Adds uids so the FK check passes in test_recieve_* tests."""
    with session_scope() as session:
        for summary in json_data:
            new_uid = User_Id(user_id = summary['userId'], 
                                active=True)
 
            #Check if UID exists in the db already
            db_uid = session.query(User_Id).filter_by(
                    user_id = new_uid.user_id).one_or_none()

            #Make sure its active if so
            if db_uid is not None:
                db_uid.active=True
            else: #Add it and an SID if not.
                session.add(new_uid)
                session.commit()
                subject = Subject(subject_id='Subject' + new_uid.user_id, 
                                  garmin_uid = new_uid.user_id)
                session.add(subject)
            

