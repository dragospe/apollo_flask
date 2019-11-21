from os import environ

import click

from flask import current_app, g
from flask.cli import with_appcontext

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

########################### Context Managers ########################
from contextlib import contextmanager

## SQLAlchemy session scoping
# See https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
# for details. Perhaps we should move this to the 'Flask-SQLalchemy' module?
#       Peter's Thoughts 2019-08-09:
#               It seems (from a cursory search of SO and some blog posts)
#               that the biggest benefit Flask-SQLalchemy provides is automatically 
#               scoping sessions to the life of a request, but this comes at the cost
#               of tightly coupling a datamodel to Flask-SQLalchemy (reducing portablility   
#               to use cases outside of flask, without additional work.) Since, ostensibly,
#               we're going to want the majority of our data in other contexts (i.e. ML) I
#               believe that using Flask-SQLalchemy for this portion of the project is
#               probably not worth it.

################################## Schemas ##############################
SCHEMA_LIST = ['garmin_oauth', 'garmin_wellness']


################################## Methods #############################

    
def init_db():
    """Deletes the database (if it exists) and recreates."""
    
    ## Create a new database (https://stackoverflow.com/questions/6506578/how-to-create-a-new-    database-using-sqlalchemy)
    # Connect to an existing, default database
    _engine = sqlalchemy.create_engine(current_app.config['DEFAULT_DATABASE_URI'])
    # Grab the underlying connection; databases can't be created inside of 
    # regular transactions
    _conn = _engine.connect()
    # Close the "connection" transaction
    _conn.execute('commit')    

    # Drop the database if it exists
    try:
        _conn.execute('DROP DATABASE "' + current_app.config['DATABASE_NAME'] + '"')
        print("INFO: Database dropped.")
    except Exception as e:
        print("INFO: Database not dropped. The following exception occured: \n\n" + str(e) + "    \n\n" )
        pass
    finally:
        _conn.execute('commit')
  
    #Create the actual database  
    _conn.execute('CREATE DATABASE "' + current_app.config['DATABASE_NAME'] + '"')
    _conn.close()    
    
    engine = current_app.config['ENGINE']
    
    # Create schemas in SCHEMA_LIST
    from sqlalchemy.schema import CreateSchema
    list(map(lambda x : engine.execute(CreateSchema(x)),SCHEMA_LIST))
    #Create tables
    import apollo_flask.db.models
    Base.metadata.create_all(engine)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')
   
def init_app(app):
    """Register database functions with the app.""" 
    app.cli.add_command(init_db_command)
    
    _Session = sessionmaker(bind = app.config['ENGINE'])
    @contextmanager
    def session_scope():
        """Provide a transactional scope around a series of database operations."""
        _session = _Session()
        try:
            yield _session
            _session.commit()
        except:
            _session.rollback()
            _session.close()
            raise
        finally:
            _session.close()

    app.session_scope = session_scope


