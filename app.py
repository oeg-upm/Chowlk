import os
import flask
from flask import request, url_for, render_template, redirect, flash, send_from_directory, current_app, session, jsonify
from flask_bootstrap import Bootstrap
import json

from converter import transform_ontology
from modules.utils import read_drawio_xml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
import argparse
from config import config


config_name = os.environ.get("APP_MODE") or "development"

app = flask.Flask(__name__)
app.config.from_object(config[config_name])
bootstrap = Bootstrap(app)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/download/<path:format>", methods=["GET", "POST"])
def download(format):
    ontology_directory = os.path.join(current_app.root_path, app.config["OUTPUT_FOLDER"])
    if format == "ttl":
        return send_from_directory(ontology_directory, session.get("ttl_filename"), as_attachment=True)
    elif format == "xml":
        return send_from_directory(ontology_directory, session.get("xml_filename"), as_attachment=True)


@app.route("/diagram_upload", methods=["GET", "POST"])
def diagram_upload():

    if request.method == "POST" and "diagram_data" in request.files:
        file = request.files["diagram_data"]
        filename = file.filename

        if filename == "":
            error = "No file choosen. Please choose a diagram."
            flash(error)
            return redirect(url_for("home"))

        root = read_drawio_xml(file)
        ttl_filename = filename[:-3] + "ttl"
        xml_filename = filename[:-3] + "owl"
        
        ttl_filepath = os.path.join(app.config["TEMPORAL_FOLDER"], ttl_filename)
        xml_filepath = os.path.join(app.config["TEMPORAL_FOLDER"], xml_filename)

        # Prueba error messaging
        new_namespaces = transform_ontology(root, ttl_filepath)

        session["ttl_filename"] = ttl_filename
        session["xml_filename"] = xml_filename

        with open(ttl_filepath, "r", encoding='utf-8') as f:
            ttl_data = f.read()
            ttl_data = ttl_data.split('\n')

        with open(xml_filepath, "r", encoding='utf-8') as f:
            xml_data = f.read()
            xml_data = xml_data.split('\n')


        return render_template("output.html", ttl_data=ttl_data, xml_data=xml_data, errors=new_namespaces)


@app.route("/api", methods=["GET", "POST"])
def api():

    if request.method == "POST":
        file = request.files["data"]
        filename = file.filename

        if filename == "":
            error = "No file choosen. Please choose a diagram."
            flash(error)
            return redirect(url_for("home"))

        root = read_drawio_xml(file)
        ttl_filename = filename[:-3] + "ttl"
        xml_filename = filename[:-3] + "owl"

        ttl_filepath = os.path.join(app.config["TEMPORAL_FOLDER"], ttl_filename)
        transform_ontology(root, ttl_filepath)

        session["ttl_filename"] = ttl_filename

        with open(ttl_filepath, "r") as f:
            ttl_data = f.read()

        return ttl_data


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])