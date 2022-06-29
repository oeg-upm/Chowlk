import os
import flask
import copy
from datetime import datetime
from flask import request, url_for, render_template, redirect, flash, send_from_directory, current_app, session, jsonify
from flask import json
from flask.helpers import make_response
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

from source.chowlk.transformations import transform_ontology
from source.chowlk.utils import read_drawio_xml
import xml.etree.ElementTree as ET
from config import config


config_name = os.environ.get("APP_MODE") or "development"

app = flask.Flask(__name__)
app.config.from_object(config[config_name])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
bootstrap = Bootstrap(app)

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Chowlk"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/api", methods=["GET", "POST"])
def api():

    if request.method == "POST":
        file = request.files["data"]
        filename = file.filename

        if filename == "":
            error = "No file choosen. Please choose a diagram."
            flash(error)
            return redirect(url_for("home"))

        os.makedirs("data", exist_ok=True)
        input_path = os.path.join("data", filename)

        ttl_filename = filename[:-3] + "ttl"

        if not os.path.exists(app.config["TEMPORAL_FOLDER"]):
            os.makedirs(app.config["TEMPORAL_FOLDER"])

        ttl_filepath = os.path.join(app.config["TEMPORAL_FOLDER"], ttl_filename)

        # Reading and transforming the diagram
        root = read_drawio_xml(file)
        turtle_file_string, xml_file_string, new_namespaces, errors = transform_ontology(root)

        # Eliminating keys that do not contain errors
        new_errors = copy.copy(errors)
        for key, error in errors.items():
            if len(error) == 0:
                del new_errors[key]

        with open(ttl_filepath, "w") as file:
            file.write(turtle_file_string)

        session["ttl_filename"] = ttl_filename

        with open(ttl_filepath, "r") as f:
            ttl_data = f.read()

        return {"ttl_data": ttl_data, "errors": new_errors, "new_namespaces": new_namespaces}


@app.errorhandler(500)
def handle_500_error(e):
    return jsonify({"error": "Server error, review the input diagram"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])