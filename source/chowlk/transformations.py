import tempfile
from source.chowlk.finding import *
from source.chowlk.associations import *
from source.chowlk.writer import *
from source.chowlk.utils import *
import rdflib
import os

def transform_ontology(root):
    finder = Finder(root)
    concepts, attribute_blocks, relations, individuals, anonymous_concepts, metadata, namespaces, rhombuses, errors = finder.find_elements()
    prefixes_identified = find_prefixes(concepts, relations, attribute_blocks, individuals)
    relations, attribute_blocks = enrich_properties(rhombuses, relations, attribute_blocks)
    attribute_blocks = resolve_concept_reference(attribute_blocks, concepts)
    associations = concept_attribute_association(concepts, attribute_blocks)
    associations, relations = concept_relation_association(associations, relations)
    individuals = individual_type_identification(individuals, associations, relations)

    file, onto_prefix, onto_uri, new_namespaces = get_ttl_template(namespaces, prefixes_identified)
    file = write_ontology_metadata(file, metadata, onto_uri)
    file = write_object_properties(file, relations, concepts, anonymous_concepts, attribute_blocks)
    file = write_data_properties(file, attribute_blocks, concepts)
    file = write_concepts(file, concepts, anonymous_concepts, associations)
    file = write_instances(file, individuals)
    file = write_general_axioms(file, concepts, anonymous_concepts)

    file.seek(os.SEEK_SET)

    g = rdflib.Graph()
    g.parse(data=file.read(), format="turtle")

    #ttl_output_filename = output_filename.split(".")[0] + ".ttl"
    #xml_output_filename = output_filename.split(".")[0] + ".owl"
    #g.serialize(destination=ttl_output_filename, format="turtle")
    #g.serialize(destination=xml_output_filename, format="xml")

    turtle_output_file = tempfile.NamedTemporaryFile()
    xml_output_file = tempfile.NamedTemporaryFile()

    g.serialize(destination=turtle_output_file, format="turtle")
    g.serialize(destination=xml_output_file, format="xml")

    turtle_output_file.seek(0)
    xml_output_file.seek(0)

    turtle_string = turtle_output_file.read().decode("utf-8")
    xml_string = xml_output_file.read().decode("utf-8")

    #file.close()
    #turtle_output_file.close()
    #xml_output_file.close()

    return turtle_string, turtle_output_file, xml_string, xml_output_file, new_namespaces, errors