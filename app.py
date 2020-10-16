import logging
import os
import flask
from flask import request, url_for, render_template, redirect
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES, DATA, ALL

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

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/diagram_upload", methods=["GET", "POST"])
def diagram_upload():

    if request.method == "POST" and "diagram_data" in request.files:
        file = request.files["diagram_data"]
        filename = file.filename

        if filename == "":
            error = "No file choosen. Please choose a diagram."
            return redirect(url_for("home"))

        logging.basicConfig(filename="logs/" + filename[:-3] + "log", level=logging.INFO)

        try:
            child_tracker = ChildTracker()
            root, root_complete, mxGraphModel, diagram, mxfile, tree = read_drawio_xml(file)
            transform_ontology(root, "tmp/" + filename[:-3] + "ttl", child_tracker)
        except Exception as e: 
            trouble_elem_id = child_tracker.get_last_child()
            root_complete = highlight_element(root_complete, trouble_elem_id)
            mxGraphModel[0] = root_complete

            try:
                diagram[0] = mxGraphModel
            except:
                diagram.text = ""
                diagram.append(mxGraphModel)

            filename = "data/problematic_diagrams/" + file.split("/")[-1]
            mxfile[0] = diagram
            ElementTree(mxfile).write(filename)
            message = "Please follow the notation specification provided at https://oeg-upm.github.io/chowlk_spec/. See the errors highlighted in red in the diagram."
            logging.error(message, e)
            logging.exception(str(e))

        ttl_filename = os.path.join("tmp", filename[:-3] + "ttl")
        with open(ttl_filename, "r", encoding='utf-8') as file:
            data = file.read()
        return render_template("output.html", data=data.split('\n'), filename=os.path.join(ttl_filename))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)