# Diagram2code (aka chOWLk)
Script to transform an ontogical diagram intro code.

###Requirements:
Install the requirements provided by:
```bash
pip install -r requirements
```
It just requires:
* beautifulsoup4==4.9.0
* soupsieve==2.0

###How to run it:
```bash
python converter.py path/diagram/xml path/output/ttlfile
```
* path/diagram/xml: is the path were you have the drawio in xml format.
* path/output/ttlfile: is the output path were to store the OWL generated ontology in ttl format.

Example of running the algorithm:
```bash
python converter.py data/kpi.xml output/kpi_owl_code.ttl
```
Currently the converter supports:
* Classes (new and reused).
* Object Properties.
* Attributes.
* Individuals.
* Namespaces.
* Ontology metadata.