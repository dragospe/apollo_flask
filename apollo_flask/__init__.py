import os
from flask import Flask

def create_app(test_config = None):
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
    
    import apollo_flask.db as db
    db.init_app(app)
    
    from . import garmin_oauth
    app.register_blueprint(garmin_oauth.bp) 

    from . import garmin_api_client
    app.register_blueprint(garmin_api_client.bp)

    return app

