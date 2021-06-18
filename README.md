![Logo](https://github.com/oeg-upm/Chowlk/blob/webservice/static/resources/logo.png)

# Chowlk Converter
Web-service to transform ontology conceptualizations made with diagrams.net into OWL code.

## How to use the web-service:

1. Go to https://chowlk.linkeddata.es/
2. Read the instructions / recomendations that your diagram should comply.
3. Click on "Choose a diagram" and select one from your local machine.
4. Click on Submit.
5. Copy-paste or download the ontology generated in TTL or in RDF/XML

## If you want to run it from the source:

### Copy the project:
```bash
git clone https://github.com/oeg-upm/Chowlk.git
git checkout webservice
```

### Requirements:
```bash
pip install -r requirements.txt
```

### To convert a diagram:
```bash
python converter.py path/to/diagram.xml output/path/ontology.ttl
```

### To run the app locally:
```bash
python app.py
```


Currently the converter only supports the <a href="https://chowlk.linkeddata.es/chowlk_spec">Chowlk visual notation</a>. Please visit the specification for more details on how to make ontology conceptualizations following the visual notation.
