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
db = SQLAlchemy(app)
CORS(app)
bootstrap = Bootstrap(app)

# Schema definition
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    input = db.Column(db.String)
    output = db.Column(db.String)
    errors = db.Column(JSON)

    def __init__(self, date, input, output, errors):
        self.date = date
        self.input = input
        self.output = output
        self.errors = errors

    def __repr__(self) -> str:
        return super().__repr__()


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

"""@app.route("/demoeswc2021", methods=["GET", "POST"])
def poster():
    return render_template("chowlk_poster.html")"""


"""@app.route("/download/<path:format>", methods=["GET", "POST"])
def download(format):
    ontology_directory = os.path.join(current_app.root_path, app.config["TEMPORAL_FOLDER"])
    if format == "ttl":
        return send_from_directory(ontology_directory, session.get("ttl_filename"), as_attachment=True)
    elif format == "xml":
        return send_from_directory(ontology_directory, session.get("xml_filename"), as_attachment=True)"""


"""@app.route("/diagram_upload", methods=["GET", "POST"])
def diagram_upload():

    if request.method == "POST" and "diagram_data" in request.files:
        file = request.files["diagram_data"]
        
        filename = file.filename

        # Verifying that there exists a file
        if filename == "":
            error = "No file choosen. Please choose a diagram."
            flash(error)
            return redirect(url_for("home"))

        os.makedirs("data", exist_ok=True)
        input_path = os.path.join("data", filename)

        # Creating the dirs to then store the output
        ttl_filename = filename[:-3] + "ttl"
        xml_filename = filename[:-3] + "owl"

        if not os.path.exists(app.config["TEMPORAL_FOLDER"]):
            os.makedirs(app.config["TEMPORAL_FOLDER"])
        
        ttl_filepath = os.path.join(app.config["TEMPORAL_FOLDER"], ttl_filename)
        xml_filepath = os.path.join(app.config["TEMPORAL_FOLDER"], xml_filename)

        # Reading and transforming the diagram
        root = read_drawio_xml(file)
        turtle_file_string, xml_file_string, new_namespaces, errors = transform_ontology(root)

        # Eliminating keys that do not contain errors
        new_errors = copy.copy(errors)
        for key, error in errors.items():
            if len(error) == 0:
                del new_errors[key]

        # Storing the output in ttl and xml
        with open(ttl_filepath, "w") as file:
            file.write(turtle_file_string)

        with open(xml_filepath, "w") as file:
            file.write(xml_file_string)

        session["ttl_filename"] = ttl_filename
        session["xml_filename"] = xml_filename


        with open(ttl_filepath, "r", encoding='utf-8') as f:
            ttl_data = f.read()
            ttl_data = ttl_data.split('\n')

        with open(xml_filepath, "r", encoding='utf-8') as f:
            xml_data = f.read()
            xml_data = xml_data.split('\n')

        user = User(datetime.now(), input_path, ttl_filepath, errors)
        db.session.add(user)
        db.session.commit()

        return render_template("output.html", ttl_data=ttl_data, xml_data=xml_data, namespaces=new_namespaces, errors=new_errors)"""


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

        user = User(datetime.now(), input_path, ttl_filepath, errors)
        db.session.add(user)
        db.session.commit()

        return {"ttl_data": ttl_data, "errors": new_errors, "new_namespaces": new_namespaces}


@app.errorhandler(500)
def handle_500_error(e):
    return jsonify({"error": "Server error, review the input diagram"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])