import os
import flask
import copy
from flask import request, url_for, render_template, redirect, flash, \
                    send_from_directory, session, jsonify
from flask_cors import CORS

from source.chowlk.transformations import transform_ontology
from source.chowlk.utils import read_drawio_xml
import xml.etree.ElementTree as ET
from config import config


config_name = os.getenv("APP_MODE", "development")

app = flask.Flask(__name__)
app.config.from_object(config[config_name])
CORS(app)

@app.route("/api", methods=["GET", "POST"])
def api():

    if request.method == "POST":
        file = request.files["data"]

        # Reading and transforming the diagram
        root = read_drawio_xml(file)
        turtle_file_string, xml_file_string, new_namespaces, errors = transform_ontology(root)

        # Eliminating keys that do not contain errors
        new_errors = copy.copy(errors)
        for key, error in errors.items():
            if len(error) == 0:
                del new_errors[key]

        return {"ttl_data": turtle_file_string, "errors": new_errors, "new_namespaces": new_namespaces}


@app.errorhandler(500)
def handle_500_error(e):
    return jsonify({"error": "Server error, review the input diagram"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])