import logging
import os
import flask
from flask import request, url_for, render_template, redirect, flash, send_from_directory, current_app, session
from flask_bootstrap import Bootstrap

from converter import transform_ontology, transform_rdf
from modules.utils import read_drawio_xml, highlight_element
from modules.child_tracker import ChildTracker
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
import argparse


app = flask.Flask(__name__)
bootstrap = Bootstrap(app)
app.config["DEBUG"] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = os.environ.get("CHOWLK_SECRET_KEY")
app.config["OUTPUT_FOLDER"] = 'tmp'
app.config["PROBLEMATIC_DIAGRAMS"] = "data/problematic_diagrams"

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/download/<path:format>", methods=["GET", "POST"])
def download(format):
    ontology_directory = os.path.join(current_app.root_path, app.config["OUTPUT_FOLDER"])
    diagram_directory = os.path.join(current_app.root_path, app.config["PROBLEMATIC_DIAGRAMS"])
    if format == "ttl":
        return send_from_directory(ontology_directory, session.get("ttl_filename"), as_attachment=True)
    elif format == "xml":
        return send_from_directory(ontology_directory, session.get("xml_filename"), as_attachment=True)
    elif format == "diagram":
        return send_from_directory(diagram_directory, session.get("diagram"), as_attachment=True)


@app.route("/diagram_upload", methods=["GET", "POST"])
def diagram_upload():

    if request.method == "POST" and "diagram_data" in request.files:
        file = request.files["diagram_data"]
        filename = file.filename

        if filename == "":
            error = "No file choosen. Please choose a diagram."
            flash(error)
            return redirect(url_for("home"))

        logging.basicConfig(filename="logs/" + filename[:-3] + "log", level=logging.INFO)

        try:
            child_tracker = ChildTracker()
            root, root_complete, mxGraphModel, diagram, mxfile, tree = read_drawio_xml(file)
            ttl_filename = filename[:-3] + "ttl"
            xml_filename = filename[:-3] + "owl"
            
            ttl_filepath = os.path.join(app.config["OUTPUT_FOLDER"], ttl_filename)
            xml_filepath = os.path.join(app.config["OUTPUT_FOLDER"], xml_filename)

            transform_ontology(root, ttl_filepath, child_tracker)
            session["ttl_filename"] = ttl_filename
            session["xml_filename"] = xml_filename

            with open(ttl_filepath, "r", encoding='utf-8') as f:
                ttl_data = f.read()
                ttl_data = ttl_data.split('\n')

            with open(xml_filepath, "r", encoding='utf-8') as f:
                xml_data = f.read()
                xml_data = xml_data.split('\n')

        except Exception as e: 
            trouble_elem_id = child_tracker.get_last_child()
            root_complete = highlight_element(root_complete, trouble_elem_id)
            mxGraphModel[0] = root_complete

            try:
                diagram[0] = mxGraphModel
            except:
                diagram.text = ""
                diagram.append(mxGraphModel)
            diagram_filepath = os.path.join(app.config["PROBLEMATIC_DIAGRAMS"], filename)
            session["diagram"] = filename
            mxfile[0] = diagram
            ElementTree(mxfile).write(diagram_filepath)
            logging.error("Error in the syntax of the diagram", e)
            logging.exception(str(e))
            ttl_data = None
            xml_data = None

        return render_template("output.html", ttl_data=ttl_data, xml_data=xml_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)