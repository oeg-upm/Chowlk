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

### 2. The API:

The following command line will return the ontology in Turtle format.

```bash
curl -F 'data=@/path/to/diagram.xml' https://chowlk.linkeddata.es/api
```

The service will return the following dictionary:

```json
{
  "ttl_data": "@prefix ns: ...",
  "new_namespaces": {"ns1": "https://namespace1.com#", "ns2": "https://namespace2.com#"},
  "errors": {"Concepts": [{"message": "Problem in text", "shape_id": "13", "value": "ns:Building Element"}],
             "Attributes": [{"message": "Problem in cardinality", "shape_id": 45, "value": "ns:ifcIdentifier"}],
             "Arrows": [],
             "Rhombuses": [],
             "Ellipses": [],
             "Namespaces": [],
             "Metadata": [],
             "Hexagons": [],
             "Individual": []}
}
```

* **ttl_data:** Contains the ontology generated from the diagram in Turtle format. It is returned in string format.
* **new_namespaces:** Contains the new namespaces created for the ontology, when prefixes are founded in the model but are not declared in the namespace block in the diagram. The returned object is a dictionary with the following format: {"prefix1": "namespace1", "prefix2": "namespace2"}
* **errors:** Contains the errors founded in the ontology diagram, organized by types. The following keywords can be founded: "Concepts", "Arrows", "Rhombuses", "Ellipses", "Attributes", "Namespaces", "Metadata", "Hexagons", "Individual". The value for these keywords is an array that may contain objects that have the following structure:

```json
{
  "message": "Some message related to the problem",
  "shape_id": "An integer id that identify the problematic shape in the diagram",
  "value": "the actual text related with the shape"
}
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
python converter.py path/to/diagram.xml output/path/ontology.ttl --type ontology --format ttl
```

* If the desired format is rdf/xml:
```bash
python converter.py path/to/diagram.xml output/path/ontology.xml --type ontology --format xml
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
