import tempfile
import sys
from app.source.chowlk.model.diagram_model import Diagram_model
from app.source.chowlk.services.individual_associations import individual_type_identification, individual_relation_association, individual_attribute_association
from app.source.chowlk.services.class_associations import concept_attribute_association, concept_relation_association
from app.source.chowlk.services.property_associations import enrich_properties
from app.source.chowlk.resources.anonymousClass import find_relations_anonymous_classes, find_attributes_anonymous_classes
from app.source.chowlk.resources.find_prefixes import find_prefixes
import rdflib

from app.source.chowlk.services.interaction_between_elements import interaction_between_elements

from app.source.chowlk.model.writer_model import Writer_model

def transform_ontology(root):
    diagram_model = Diagram_model()
    diagram_model.classify_elements(root)
    interaction_between_elements(diagram_model)
    enrich_properties(diagram_model)
    prefixes_identified = find_prefixes(diagram_model)
    associations = concept_attribute_association(diagram_model)
    associations = concept_relation_association(associations, diagram_model)
    find_relations_anonymous_classes(diagram_model)
    find_attributes_anonymous_classes(diagram_model)
    individual_type_identification(diagram_model)
    associations_individuals = individual_relation_association(diagram_model)
    associations_individuals = individual_attribute_association(associations_individuals, diagram_model)
    writer_model = Writer_model()
    file, new_namespaces, base_uri = writer_model.write_ontology(diagram_model, prefixes_identified, associations, associations_individuals)

    ontology_uri = diagram_model.get_ontology_uri()
    errors = diagram_model.get_errors()
    warnings = diagram_model.get_warnings()

    turtle_output_file = tempfile.NamedTemporaryFile()
    xml_output_file = tempfile.NamedTemporaryFile()

    file.seek(0)
    file_read = file.read()

    if base_uri[-1] != '#':
        file_read = file_read.replace('<#', "<")
    
    try:
        g = rdflib.Graph()
        g.parse(data=file_read, format="turtle")

        g.serialize(destination=turtle_output_file, format="turtle")
        g.serialize(destination=xml_output_file, base = base_uri, format="xml")

        turtle_output_file.seek(0)
        xml_output_file.seek(0)

        turtle_string = turtle_output_file.read().decode("utf-8")
        turtle_string = turtle_string.replace('<>', '<' + ontology_uri + '>')

        xml_string = xml_output_file.read().decode("utf-8")

    except:

        errors["Syntax"] = {
            "message": "Please check your syntax on the diagram, here you have a hint of  \
                    the possible error:\n" + str(sys.exc_info()[1])
        }

        turtle_string = file_read
        xml_string = file_read

    turtle_string = turtle_string.replace('##', '#')

    return turtle_string, xml_string, new_namespaces, errors, warnings


