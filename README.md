![Logo](https://github.com/oeg-upm/Chowlk/blob/webservice/static/resources/logo.png)

# Chowlk Converter
Tool to transform ontology conceptualizations made with diagrams.net into OWL code.

The conceptualizations should follow the <a href="https://chowlk.linkeddata.es/chowlk_spec">Chowlk visual notation</a>. Please visit the specification for more details.

## How to use the tool

You have several options to use this tool.

### 1. The web application:

1. Go to https://chowlk.linkeddata.es/ web application.
2. Read the instructions / recomendations that your diagram should comply.
3. Click on "Choose a diagram" and select one from your local machine.
4. Click on Submit.
5. Copy-paste or download the ontology generated in TTL or in RDF/XML.

### 2. The web service:

The following command line will return the ontology in Turtle format.

```bash
curl -F 'data=@/path/to/diagram.xml' https://chowlk.linkeddata.es/api
```

### 3. Running it from source:

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

* If the desired format is ttl:
```bash
python converter.py path/to/diagram.xml output/path/ontology.ttl --format ttl
```

* If the desired format is rdf/xml:
```bash
python converter.py path/to/diagram.xml output/path/ontology.ttl --format xml
```

### To run the app locally:
```bash
python app.py
```

## Publications
Chávez-Feria, S., García-Castro, R., Poveda-Villalón, M. (2021). <i>Converting UML-based ontology conceptualizations to OWL with Chowlk. In ESWC (Poster and Demo Track)</i>



## Contact
* Serge Chávez-Feria (serge.chavez.feria@upm.es)
* Maria Poveda-Villalón (mpoveda@fi.upm.es)
