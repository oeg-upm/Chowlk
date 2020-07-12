import logging
import os
import flask
from flask import request, url_for, render_template
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES, DATA, ALL

from converter import transform_ontology, transform_rdf
from modules.utils import read_drawio_xml



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

        logging.basicConfig(filename="logs/" + filename[:-3] + "log", level=logging.INFO)
        
        try:
            root = read_drawio_xml(file)
            transform_ontology(root, "tmp/" + filename[:-3] + "ttl")
        except Exception as e:
            logging.error("Error occurred", e)
            logging.exception(str(e))
    
    with open("tmp/" + filename[:-3] + "ttl", "r") as file:
        data = file.read()
    #return render_template("output.html", data=data)
    return render_template("output.html")

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)