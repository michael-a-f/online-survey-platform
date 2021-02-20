import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Creates a global instance of flask_login's LoginManager to be used in User class.
login_manager = LoginManager()

# Creates a global instance of sqlalchemy.
#db = SQLAlchemy()

def create_app(test_config=None):
    """Create and configure the app.

    Application factory style used here to make sure there is no global
    instance of app. This is much more practical way of creating the
    application instance and allows for integration of blueprints and easier
    deployment to a web server.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    login_manager.init_app(app)

    # blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import views
    app.register_blueprint(views.bp)

    from . import create
    app.register_blueprint(create.bp)

    from . import answer
    app.register_blueprint(answer.bp)

    return app


    