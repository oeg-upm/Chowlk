import zlib
import xml.etree.ElementTree as ET
import base64
from urllib.parse import unquote
import os
import copy
import re

tree = ET.parse("data/kpi.xml")
mxfile = tree.getroot()
root = mxfile[0][0][0]

"""
# This lines are for compresed XML files
compressed_xml = root[0].text
coded_xml = base64.b64decode(compressed_xml)
xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))
mxGraphModel = ET.fromstring(xml_string)
"""

def get_corners(x, y, width, height):
    x, y, width, height = int(x), int(y), int(width), int(height)
    p1 = (x, y)
    p2 = (x, y+height)
    p3 = (x+width, y)
    p4 = (x+width, y+height)

    return p1, p2, p3, p4

def find_elements(root):

    concepts = []
    attributes = []
    relations = []

    for child in root:
        try:
            edge = child.attrib["edge"]
        except:
            edge = None
        if edge is None:
            if child.attrib["id"] in ["0", "1"]:
                continue
            style = child.attrib["style"]
            if "fillColor" in style:
                concepts.append(child)
            else:
                attributes.append(child)
        else:
            relations.append(child)

    return concepts, attributes, relations

def concept_attribute_association(root):

    concepts, attributes, _ = find_elements(root)
    concept_paired = False
    pairs = []

    for concept in concepts:
        for geom_obj in concept:
            x, y = geom_obj.attrib["x"], geom_obj.attrib["y"]
            width, height = geom_obj.attrib["width"], geom_obj.attrib["height"]
            _, p2_concept, _, _ = get_corners(x, y, width, height)
        for attribute in attributes:
            for geom_obj in attribute:
                x, y = geom_obj.attrib["x"], geom_obj.attrib["y"]
                width, height = geom_obj.attrib["width"], geom_obj.attrib["height"]
                p1_attrib, _, _, _ = get_corners(x, y, width, height)

            dx = abs(p2_concept[0] - p1_attrib[0])
            dy = abs(p2_concept[1] - p1_attrib[1])

            if dx < 5 and dy < 5:
                pairs.append({"concept": concept, "attribute": attribute})
                concept_paired = True
                break

        if concept_paired == False:
            pairs.append({"concept": concept})

        else: concept_paired = False

    return pairs

def concept_relation_association(concept_attribute_pairs, relations):

    concept_atr_rel_triplets = copy.deepcopy(concept_attribute_pairs)
    for relation in relations:
        source_id = relation.attrib["source"]
        target_id = relation.attrib["target"]
        for i, pair in enumerate(concept_attribute_pairs):
            concept_id = pair["concept"].attrib["id"]
            try:
                attribute_id = pair["concept"].attrib["id"]
            except:
                attribute_id = None
            if concept_id == source_id or attribute_id == source_id:
                concept_atr_rel_triplets[i]["relation"] = {"link": relation}
                break

        for j, pair in enumerate(concept_attribute_pairs):
            concept_id = pair["concept"].attrib["id"]
            try:
                attribute_id = pair["concept"].attrib["id"]
            except:
                attribute_id = None
            if concept_id == target_id or attribute_id == target_id:
                concept_atr_rel_triplets[i]["relation"]["target_concept"] = pair["concept"]
                break

    return concept_atr_rel_triplets

def get_ttl_template(filename, onto_uri):

    file = open(filename, 'w')
    file.write("@prefix : " + onto_uri + " .\n")
    file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
               "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
               "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
               "@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n"
               "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")

    file.write(onto_uri + " rdf:type owl:Ontology .\n\n")

    return file


filename = "owl_code.ttl"
onto_uri = "<http://example.org/ontology#>"

concepts, attributes, relations = find_elements(root)
pairs = concept_attribute_association(root)
triplets = concept_relation_association(pairs, relations)

file = get_ttl_template(filename, onto_uri)

file.write("#################################################################\n"
           "#    Object Properties\n"
           "#################################################################\n\n")

for relation in relations:

    index_sufix = relation.attrib["value"].find("(")
    index_prefix = relation.attrib["value"].find(":")
    relation_name_without_prefix = relation.attrib["value"][index_prefix+1:index_sufix-1]
    relation_name_with_prefix = relation.attrib["value"][:index_sufix-1]
    file.write("### " + onto_uri[1:-1] + relation_name_without_prefix + "\n")
    file.write(relation_name_with_prefix + " rdf:type owl:ObjectProperty .\n\n")


file.write("#################################################################\n"
           "#    Datatype Properties\n"
           "#################################################################\n\n")

for attribute in attributes:

    splitted_attributes = re.split("<br>", attribute.attrib["value"])
    for real_attribute in splitted_attributes:
        index_prefix = real_attribute.find(":")
        index_sufix = real_attribute.find("::")
        cardinality_limit_1 = real_attribute.find("(")
        cardinality_limit_2 = real_attribute.find(")")
        cardinality_sep = real_attribute.find("..")
        max_cardinality = real_attribute[cardinality_sep+2:cardinality_limit_2]
        attrib_name_without_prefix = real_attribute[index_prefix + 1:index_sufix]
        attrib_name_with_prefix = real_attribute[cardinality_limit_2 + 1:index_sufix]
        file.write("### " + onto_uri[1:-1] + attrib_name_without_prefix + "\n")
        if max_cardinality == "1":
            file.write(attrib_name_with_prefix + " rdf:type owl:DatatypeProperty ,\n")
            file.write("\t\t\towl:FunctionalProperty .\n\n")
        else:
            file.write(attrib_name_with_prefix + " rdf:type owl:DatatypeProperty .\n\n")


file.write("#################################################################\n"
           "#    Classes\n"
           "#################################################################\n\n")

for triplet in triplets:

    concept = triplet["concept"]
    concept_name_without_prefix = concept.attrib["value"][concept.attrib["value"].find(":")+1:]
    concept_name_with_prefix = concept.attrib["value"]
    file.write("### " + onto_uri[1:-1] + concept_name_without_prefix + "\n")
    file.write(concept_name_with_prefix + " rdf:type owl:Class .\n\n")



"""
for child in root:
    print(child.tag, child.attrib)

    try:
        edge = child.attrib["edge"]
    except:
        edge = None

    if edge is not None:
        source = child.attrib["source"]
        target = child.attrib["target"]
        link_value = child.attrib["value"][:-7]

        property_line = link_value + " rdf:type owl:ObjectProperty ."
        file.write(property_line + "\n" + "\n")

        for child in root:
            if child.attrib["id"] == source:
                source_value = child.attrib["value"]

            elif child.attrib["id"] == target:
                target_value = child.attrib["value"]

        class_line = source_value + " rdf:type owl:Class ;"
        subclass_line = "\trdfs:subClassOf [ rdf:type owl:Restriction; \n" \
                        "\towl:onProperty {} ; \n" \
                        "\towl:someValuesFrom {} ] .".format(link_value, target_value)
        file.write(class_line + "\n")
        file.write(subclass_line + "\n" + "\n")

"""