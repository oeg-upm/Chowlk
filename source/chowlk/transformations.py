import tempfile
import sys
from source.chowlk.finding import *
from source.chowlk.associations import *
from source.chowlk.writer import *
from source.chowlk.utils import *
from source.chowlk.anonymousClass import *
import rdflib
import os
import re


def transform_ontology(root):
    finder = Finder(root)
    concepts, attribute_blocks, relations, individuals, anonymous_concepts, hexagons, metadata, namespaces, rhombuses, errors, anonimous_classes = finder.find_elements()
    """print("\n concepts")
    print(concepts)
    print("\n attribute_blocks")
    print(attribute_blocks)
    print("\n relations")
    print(relations)
    print("\n individuals")
    print(individuals)
    print("\n hexagons")
    print(hexagons)
    print("\n anonymous_concepts")
    print(anonymous_concepts)
    print("\n metadata")
    print(metadata)
    print("\n namespaces")
    print(namespaces)
    print("\n rhombuses")
    print(rhombuses)
    print("\n anonymous classes")
    print(anonimous_classes)"""
    values = finder.find_attribute_values()
    """print("\n values")
    print(values)"""
    prefixes_identified = find_prefixes(concepts, relations, attribute_blocks, individuals)
    relations, attribute_blocks = enrich_properties(rhombuses, relations, attribute_blocks, concepts)
    attribute_blocks = resolve_concept_reference(attribute_blocks, concepts)
    associations = concept_attribute_association(concepts, attribute_blocks)
    associations, relations = concept_relation_association(associations, relations)
    individuals = individual_type_identification(individuals, associations, relations, hexagons, errors)
    individuals = individual_type_identification_rdf(individuals, concepts, relations)
    associations_individuals = individual_relation_association(individuals, relations)
    associations_individuals = individual_attribute_association(associations_individuals, values, relations)
    file, onto_prefix, onto_uri, new_namespaces, errors = get_ttl_template(namespaces, prefixes_identified, errors)
    """print("\n relations")
    print(relations)
    print("\n associations")
    print(associations)"""
    anonimous_classes = find_relations_anonymous_classes(relations, anonimous_classes)
    """print("\n anonymous classes")
    print(anonimous_classes)"""
    file = write_ontology_metadata(file, metadata, onto_uri)
    file, errors = write_object_properties(file, relations, concepts, anonymous_concepts, attribute_blocks, hexagons, individuals, errors)
    file = write_data_properties(file, attribute_blocks, concepts)
    """print("\n hexagons")
    print(hexagons)"""
    file = write_concepts(file, concepts, anonymous_concepts, associations,individuals, hexagons, errors, relations, anonimous_classes)
    file = write_instances(file, individuals)
    file = write_triplets(file, individuals, associations_individuals, values)
    file = write_general_axioms(file, concepts, anonymous_concepts, individuals, hexagons)

    # print(file.read())
    # file.seek(os.SEEK_SET)

    turtle_output_file = tempfile.NamedTemporaryFile()
    xml_output_file = tempfile.NamedTemporaryFile()

    file.seek(0)
    file_read = file.read()

    # Prueba
    f = open("demofile2.txt", "w")
    f.write(file_read)
    f.close()

    # Change cambiar_a_base prefix by base directive
    file_read = file_read.replace("<cambiar_a_base:", "<" + onto_uri)
    #file_read = re.sub("<cambiar_a_base:", "<" + onto_uri, file_read)

    # Change cambiar_a_prefijo_vacio prefix by empty prefix(":")
    file_read = file_read.replace("cambiar_a_prefijo_vacio:", ":")

    # Prueba
    f = open("demofile3.txt", "w")
    f.write(file_read)
    f.close()

    try:
        g = rdflib.Graph()
        g.parse(data=file_read, format="turtle")

        g.serialize(destination=turtle_output_file, format="turtle")
        g.serialize(destination=xml_output_file, format="xml")

        turtle_output_file.seek(0)
        xml_output_file.seek(0)

        turtle_string = turtle_output_file.read().decode("utf-8")
        xml_string = xml_output_file.read().decode("utf-8")

    except:
        print("Please check your syntax on the diagram, here you have a hint of the possible error:")
        print(sys.exc_info()[1])

        errors["Syntax"] = {
            "message": "Please check your syntax on the diagram, here you have a hint of  \
                    the possible error:\n" + str(sys.exc_info()[1])
        }

        turtle_string = file_read
        xml_string = file_read

    return turtle_string, xml_string, new_namespaces, errors


"""def transform_rdf(root):

    finder = Finder(root)
    individuals = finder.find_individuals()
    relations = finder.find_relations()
    namespaces = finder.find_namespaces()
    values = finder.find_attribute_values()
    concepts, attribute_blocks = finder.find_concepts_and_attributes()

    prefixes_identified = find_prefixes(concepts, relations, attribute_blocks, individuals)

    individuals = individual_type_identification_rdf(individuals, concepts, relations)
    
    associations_individuals = individual_relation_association(individuals, relations)
    associations_individuals = individual_attribute_association(associations_individuals, values, relations)
    file, onto_prefix, onto_uri, new_namespaces = get_ttl_template(namespaces, prefixes_identified)

    file = write_triplets(file, individuals, associations_individuals, values)

    file.seek(os.SEEK_SET)

    g = rdflib.Graph()
    g.parse(data=file.read(), format="turtle")

    turtle_output_file = tempfile.NamedTemporaryFile()
    xml_output_file = tempfile.NamedTemporaryFile()

    g.serialize(destination=turtle_output_file, format="turtle")
    g.serialize(destination=xml_output_file, format="xml")

    turtle_output_file.seek(0)
    xml_output_file.seek(0)

    turtle_string = turtle_output_file.read().decode("utf-8")
    xml_string = xml_output_file.read().decode("utf-8")

    return turtle_string, xml_string"""
