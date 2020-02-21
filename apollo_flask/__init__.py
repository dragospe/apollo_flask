"""
This module provides an app factory for apollo_flask.
"""

import os
from flask import Flask, render_template, current_app

def create_app(test_config=None):
    """
    This function is an app_factory for apollo_flask.

    Configuration is passed in via one of three ways:
        - via `instance/config.py` when the code is not installed as a module
        - via '.../var/apollo_flask-instance/config.py`, if installed as a module
               via pip (possibly under a virtual environment)
        - via a dictionary passed in a the test_conifg kwarg.

    Once the configuration is loaded, the database is attached to the application.

    Then, routes and blueprints are added, and an app is returned.
    """
    #Second argument ensures configuration is loaded from the instance folder
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=False)
    else:
        # load the test_config if it was passed in
        app.config.from_mapping(test_config)

    #ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Set up database
    import apollo_flask.db as db
    app.config['ENGINE'] = db.create_engine(app.config['DATABASE_URI'])
    db.init_app(app)

    @app.route('/')
    def homepage():
        return render_template('index.html',
                               project_name=current_app.config['PROJECT_NAME'])

    from . import garmin_oauth
    app.register_blueprint(garmin_oauth.bp)

    from . import garmin_api_client
    app.register_blueprint(garmin_api_client.bp)

    return app
