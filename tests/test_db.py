"""This file tests some basic database functions. To do so, it also incidentally 
tests some functions from the garmin_oauth.__init__ file when constructing,
adding, and querying objects from the database.
""" 


from apollo_flask import db
from apollo_flask.db.models import * 
import os
import time
import pytest
from flask import current_app

############## Tests #####################

class DummyException(Exception):
    """A do-nothing exception for testing try/except clasuses."""
    pass

def test_successful_session_scope(app):
    """Ensure a scoped session commits and rolls back appropriately. After
    each operation, make sure the session was closed successfully."""

    session_scope = app.config['SESSION_SCOPE_FUNC']

    uid = garmin_oauth.User_Id(user_id = 'test_session_scope_user_id', active= True)
    
    #Check that commits happen properly
    with session_scope() as session:
        session.add(uid)    

    with session_scope() as session:
        uid= session.query(garmin_oauth.User_Id).filter_by(
            user_id = 'test_session_scope_user_id').first()
        assert uid ##make sure it's present
        assert repr(uid) == "<Garmin_User_ID(user_id = 'test_session_scope_user_id', access_tokens = '[]', active = 'True')>"         

    #Check that rollbacks happen properly
    ## This is a tricky setup. We need to raise an exception here to ensure that
    ## session_scope rolls back properly, but we can't catch the exception that
    ## is raised manually (because then it won't be passed to session scope, 
    ## the rollback won't happen, and the connection won't be closed). 
    ##
    ## What we do instead is raise the exception inside the session_scope
    ## context manager, let the session scope catch it and re-raise it,
    ## and then catch it with the pytest.raises context manager.
    with pytest.raises(DummyException):
        with session_scope() as session:
            session.add(garmin_oauth.User_Id(user_id = 'roll_me_back', active = True))
            raise(DummyException)

    with session_scope() as session:
        assert not session.query(garmin_oauth.User_Id).filter_by(user_id = 'roll_me_back').first()

    #Clean up
    with session_scope() as session:
        session.delete(uid)


def test_init_db(app):
    #Check that schema were appropriate loaded
    from sqlalchemy.engine import reflection
    insp = reflection.Inspector.from_engine(app.config['ENGINE'])
    assert db.SCHEMA_LIST.sort() == insp.get_schema_names().sort()


def test_init_db_command(runner, monkeypatch):
    #Replace the init_db click command with one that records if it's been called.
    #Check that the output is as expected
    #(Test taken directly  from the flask tutorial)
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('apollo_flask.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

    
