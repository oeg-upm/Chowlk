from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(settings_module):
    app = Flask(__name__)

    # Load the config file specified by the APP environment variable
    app.config.from_object(settings_module)

    db.init_app(app)

    #register blueprints
    from .public import public_bp
    app.register_blueprint(public_bp)

    return app
