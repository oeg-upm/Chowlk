import argparse
from modules.finding import *
from modules.associations import *
from modules.writer import *
from modules.utils import *
import rdflib
import rdflib.serializer


def transform_ontology(root, output_filename):
    finder = Finder(root)
    concepts, attribute_blocks, relations, individuals, anonymous_concepts, metadata, namespaces, rhombuses, errors = finder.find_elements()
    prefixes_identified = find_prefixes(concepts, relations, attribute_blocks, individuals)
    relations, attribute_blocks = enrich_properties(rhombuses, relations, attribute_blocks)
    attribute_blocks = resolve_concept_reference(attribute_blocks, concepts)
    associations = concept_attribute_association(concepts, attribute_blocks)
    associations, relations = concept_relation_association(associations, relations)
    individuals = individual_type_identification(individuals, associations, relations)

    file, onto_prefix, onto_uri, new_namespaces = get_ttl_template(output_filename, namespaces, prefixes_identified)
    file = write_ontology_metadata(file, metadata, onto_uri)
    file = write_object_properties(file, relations, concepts, anonymous_concepts, attribute_blocks)
    file = write_data_properties(file, attribute_blocks, concepts)
    file = write_concepts(file, concepts, anonymous_concepts, associations)
    file = write_instances(file, individuals)
    file = write_general_axioms(file, concepts, anonymous_concepts)

    g = rdflib.Graph()
    with open(output_filename, "r") as file:
        g.parse(file, format="turtle")

    ttl_output_filename = output_filename.split(".")[0] + ".ttl"
    xml_output_filename = output_filename.split(".")[0] + ".owl"
    g.serialize(destination=ttl_output_filename, format="turtle")
    g.serialize(destination=xml_output_filename, format="xml")
    
    turtle_file = open(ttl_output_filename, "r")
    turtle_file_string = turtle_file.read()

    return turtle_file_string, new_namespaces, errors
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("diagram_path")
    parser.add_argument("output_path")
    args = parser.parse_args()

    root = read_drawio_xml(args.diagram_path)
    transform_ontology(root, args.output_path)
