import xml.etree.ElementTree as ET
import argparse
from modules.finding import *
from modules.associations import *
from modules.writer import *
from modules.utils import read_drawio_xml

"""
# This lines are for compresed XML files
compressed_xml = root[0].text
coded_xml = base64.b64decode(compressed_xml)
xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))
mxGraphModel = ET.fromstring(xml_string)
"""


def transform_ontology(root, filename):

    all_elements = find_elements(root)
    concepts, attribute_blocks, relations = all_elements[0:3]
    individuals, anonymous_concepts, ontology_metadata, namespaces = all_elements[3:]
    attribute_blocks = resolve_concept_reference(attribute_blocks, concepts)

    associations = concept_attribute_association(concepts, attribute_blocks)
    associations, relations = concept_relation_association(associations, relations)
    individuals = individual_type_identification(individuals, associations, relations)

    file, onto_prefix, onto_uri = get_ttl_template(filename, namespaces)
    file = write_ontology_metadata(file, ontology_metadata, onto_uri)
    file = write_object_properties(file, relations, concepts, anonymous_concepts)
    file = write_data_properties(file, attribute_blocks, concepts)
    file = write_concepts(file, concepts, anonymous_concepts, associations)
    file = write_instances(file, individuals)
    file = write_general_axioms(file, concepts, anonymous_concepts)


def transform_rdf(root, filename):

    individuals = find_individuals(root)
    relations = find_relations(root)
    namespaces = find_namespaces(root)
    values = find_attribute_values(root)
    concepts, _ = find_concepts_and_attributes(root)

    individuals = individual_type_identification_rdf(individuals, concepts, relations)
    associations = individual_relation_association(individuals, relations)
    associations = individual_attribute_association(associations, values, relations)

    file, onto_prefix, onto_uri = get_ttl_template(filename, namespaces)

    for id, association in associations.items():

        subject = association["individual"]["prefix"] + ":" + association["individual"]["uri"]
        concept = association["individual"]["type"]
        relations = association["relations"]

        file.write(subject + " rdf:type " + concept)

        for relation_id, relation in relations.items():
            file.write(" ;\n")
            predicate = relation["prefix"] + ":" + relation["uri"]
            target_id = relation["target"]
            object = individuals[target_id]["prefix"] + ":" + individuals[target_id]["uri"]

            file.write("\t" + predicate + " " + object)

        file.write(" .\n\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("diagram_path")
    parser.add_argument("output_path")
    parser.add_argument("type")
    args = parser.parse_args()

    root = read_drawio_xml(args.diagram_path)

    if args.type == "ontology":
        transform_ontology(root, args.output_path)
    elif args.type == "rdf":
        transform_rdf(root, args.output_path)
    else:
        raise ValueError("Not a correct option of data")