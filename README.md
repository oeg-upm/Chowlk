# Diagram2code (aka chOWLk)
Script to transform an ontogical diagram intro code.

### Requirements:
Install the requirements provided by:
```bash
pip install -r requirements.txt
```
It just requires:
* beautifulsoup4==4.9.0
* soupsieve==2.0

### How to run it:
```bash
python converter.py path/diagram/xml path/output/ttlfile mode
```
* path/diagram/xml: is the path where you have the drawio in xml format.
* path/output/ttlfile: is the output path to store the OWL generated ontology in ttl format.
* mode: indicates whether to transform an ontological or a rdf diagram.

Example of running the algorithm:
```bash
python converter.py data/kpi.xml output/kpi_owl_code.ttl ontology
```
Currently the converter supports:
* Classes (new and reused).
* Object Properties.
* Attributes.
* Individuals.
* Namespaces.
* Ontology metadata.
