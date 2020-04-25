import zlib
import xml.etree.ElementTree as ET
import base64
from urllib.parse import unquote
import os
import copy
import re
import html
import bs4
from bs4 import BeautifulSoup
import math



"""
# This lines are for compresed XML files
compressed_xml = root[0].text
coded_xml = base64.b64decode(compressed_xml)
xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))
mxGraphModel = ET.fromstring(xml_string)
"""

def get_corners(x, y, width, height):

    p1 = (x, y)
    p2 = (x, y+height)
    p3 = (x+width, y)
    p4 = (x+width, y+height)

    return p1, p2, p3, p4

def find_missing_source_target(property_restrictions, object_properties, sources_targets):

    """ Function to find the source and target of floating edges, for now it only works for
    edges that support the relation between two other edges, it can be extended for other cases"""

    # Under this scope restrictions are all relations that indicate relationships
    # between other object properties
    for restriction in property_restrictions:

        child = restriction["xml_object"]

        geom_property = child[0]
        for elem in geom_property:
            if elem.attrib["as"] == "sourcePoint":
                x_source, y_source = float(elem.attrib["x"]), float(elem.attrib["y"])
            elif elem.attrib["as"] == "targetPoint":
                x_target, y_target = float(elem.attrib["x"]), float(elem.attrib["y"])

        # Iteration to look for other edges as possibles sources
        for property in object_properties:
            child2 = property["xml_object"]
            #for child2 in root:
            # We are considering the simple scenario in which the supporting or
            # reference edges have source and target, however this is not always the situation
            #source_child2 = child2.attrib["source"]
            #target_child2 = child2.attrib["target"]
            source_child2 = property["source"]
            target_child2 = property["target"]

            # Look for the source object and extract its geometry
            for shape in sources_targets:
                #for child3 in root:
                child3 = shape["xml_object"]
                if source_child2 == shape["id"]:
                    s_shape_x, s_shape_y = child3[0].attrib["x"], child3[0].attrib["y"]
                    s_shape_width, s_shape_height = child3[0].attrib["width"], child3[0].attrib["height"]
                    break
            # Now compute the geometry of the initial source point of the edge
            exitX = child2.attrib["style"].split("exitX=")[1].split(";")[0]
            exitY = child2.attrib["style"].split("exitY=")[1].split(";")[0]
            x_source_ref = float(s_shape_x) + float(s_shape_width) * float(exitX)
            y_source_ref = float(s_shape_y) + float(s_shape_height) * float(exitY)
            source_point_ref = [x_source_ref, y_source_ref]

            # Look for the target object and extract its geometry
            for shape in sources_targets:
                #for child3 in root:
                if target_child2 == shape["id"]:
                    t_shape_x, t_shape_y = child3[0].attrib["x"], child3[0].attrib["y"]
                    t_shape_width, t_shape_height = child3[0].attrib["width"], child3[0].attrib["height"]
                    break
            # Now compute the geometry of the initial source point of the edge
            entryX = child2.attrib["style"].split("entryX=")[1].split(";")[0]
            entryY = child2.attrib["style"].split("entryY=")[1].split(";")[0]
            x_target_ref = float(t_shape_x) + float(t_shape_width) * float(entryX)
            y_target_ref = float(t_shape_y) + float(t_shape_height) * float(entryY)
            target_point_ref = [x_target_ref, y_target_ref]

            # We have to determine how many inflexion points it have, however sometimes it is
            # not indicated explicitly and have to be derived from the associated shapes.
            # Try to iter over the mxGeom elements, if they exist
            elem = [i for i in child2[0] if i.attrib["as"] == "points"]
            # if you found an element with the attribute "points", Eureka!
            if len(elem) != 0:
                #for elem in child2[0]:
                #if elem.attrib["as"] == "points":
                elem = elem[0]
                points_ref = []
                for mxPoint in elem:
                    point = [float(mxPoint.attrib["x"]), float(mxPoint.attrib["y"])]
                    points_ref.append(point)
                points_ref.insert(0, source_point_ref)
                points_ref.append(target_point_ref)

                # At this point you already have all the points for a candidate line
                # We are going to evaluate each segment of the candidate line
                for index in range(len(points_ref) - 1):
                    point_A = points_ref[index]
                    point_B = points_ref[index + 1]

                    if point_A[0] > point_B[0]:
                        min_x, max_x = point_B[0], point_A[0]
                    else:
                        min_x, max_x = point_A[0], point_B[0]

                    if point_A[1] > point_B[1]:
                        min_y, max_y = point_B[1], point_A[1]
                    else:
                        min_y, max_y = point_A[1], point_B[1]

                    if restriction["source"] is None:
                        if x_source > min_x - 5 and x_source < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_source > min_y - 5 and y_source < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["source"] = property["id"]
                            break
                    if restriction["target"] is None:
                        if x_target > min_x - 5 and x_target < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_target > min_y - 5 and y_target < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["target"] = property["id"]
                            break

                if restriction["source"] is not None and restriction["target"] is not None:
                    break

            else:
                # Sometimes we have straight lines and the process is simple to evaluate
                if x_source_ref == x_target_ref or y_source_ref == y_target_ref:

                    point_A = [x_source_ref, y_source_ref]
                    point_B = [x_target_ref, y_target_ref]

                    if point_A[0] > point_B[0]:
                        min_x, max_x = point_B[0], point_A[0]
                    else:
                        min_x, max_x = point_A[0], point_B[0]

                    if point_A[1] > point_B[1]:
                        min_y, max_y = point_B[1], point_A[1]
                    else:
                        min_y, max_y = point_A[1], point_B[1]

                    if restriction["source"] is None:
                        if x_source > min_x - 5 and x_source < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_source > min_y - 5 and y_source < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["source"] = property["id"]
                            break
                    if restriction["target"] is None:
                        if x_target > min_x - 5 and x_target < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_target > min_y - 5 and y_target < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["target"] = property["id"]
                            break


def find_elements(root):

    concepts = []
    attribute_blocks = []
    relations = []
    individuals = []
    anonymous_concepts = []
    ontology_metadata = {}
    namespaces = {}

    for child in root:

        if child.attrib["id"] in ["0", "1"]:
            continue

        id = child.attrib["id"]
        style = child.attrib["style"]
        value = child.attrib["value"] if "value" in child.attrib else None
        discard_edge = False
        attributes_found = False

        if "edge" in child.attrib:
            relation = {}
            source = child.attrib["source"] if "source" in child.attrib else None
            target = child.attrib["target"] if "target" in child.attrib else None

            relation["source"] = source
            relation["target"] = target  # (Then Evaluate what happen if they do not have target or source)
            relation["id"] = id
            relation["xml_object"] = child

            if value == "" or value is None:

                # Looking for ellipses in a second iteration
                for child2 in root:
                    if source == child2.attrib["id"] and "ellipse" in child2.attrib["style"]:
                        # This edge is part of a unionOf / intersectionOf construct
                        # it is not useful beyond that construction
                        discard_edge = True
                        break
                if discard_edge:
                    continue

                # Sometimes edges have their value not embedded into the edge itself, at least not in the
                # "value" parameter of the object. We can track their associated value by looking for free text
                # and evaluating the "parent" parameter which will point to an edge.
                for child2 in root:
                    if "text" in child2.attrib["style"] and id == child2.attrib["parent"]:
                        value = child2.attrib["value"]
                        break

                # If after the evaluation of free text we cannot find any related text to the edge
                # we can say for sure that it is a "subclass" or "type" relationship
                if value == "" or value is None:
                    # Check for both sides of the edge, sometimes it can be tricky.
                    if "endArrow=block" in style or "startArrow=block" in style:
                        relation["type"] = "rdfs:subClassOf"
                    elif "endArrow=open" in style or "startArrow=open" in style:
                        relation["type"] = "rdf:type"
                    relations.append(relation)
                    continue

            if "subClassOf" in value:
                relation["type"] = "rdfs:subClassOf"
                relations.append(relation)
                continue
            if "type" in value:
                relation["type"] = "rdf:type"
                relations.append(relation)
                continue
            if "equivalentClass" in value:
                relation["type"] = "owl:equivalentClass"
                relations.append(relation)
                continue
            if "disjointWith" in value:
                relation["type"] = "owl:disjointWith"
                relations.append(relation)
                continue
            if "subPropertyOf" in value:
                relation["type"] = "owl:subPropertyOf"
                relations.append(relation)
                continue
            if "equivalentProperty" in value:
                relation["type"] = "owl:equivalentProperty"
                relations.append(relation)
                continue
            if "inverseOf" in value:
                relation["type"] = "owl:inverseOf"
                relations.append(relation)
                continue

            # Domain Range evaluation
            if "dashed=1" in style and "startArrow=oval" not in style:
                relation["domain"] = False
                relation["range"] = False
            elif "dashed=1" in style and "startFill=0" in style:
                relation["domain"] = False
                relation["range"] = False
            elif "dashed=1" not in style and "startArrow=oval" not in style:
                relation["domain"] = True
                relation["range"] = True
            elif "dashed=1" not in style and "startFill=1" in style:
                relation["domain"] = True
                relation["range"] = True
            elif "dashed=1" in style and "startFill=1" in style:
                relation["domain"] = True
                relation["range"] = False
            elif "dashed=1" not in style and "startFill=0" in style:
                relation["domain"] = False
                relation["range"] = True
            # Existential Universal restriction evaluation
            if "allValuesFrom" in value or "(all)" in value or "∀" in value:
                relation["allValuesFrom"] = True
            else:
                relation["allValuesFrom"] = False
            if "someValuesFrom" in value or "(some)" in value or "∃" in value:
                relation["someValuesFrom"] = True
            else:
                relation["someValuesFrom"] = False

            # Property restriction evaluation
            relation["functional"] = True if "(F)" in value else False
            relation["inverse_functional"] = True if "(IF)" in value else False
            relation["transitive"] = True if "(T)" in value else False
            relation["symmetric"] = True if "(S)" in value else False

            # Finding the property uri
            relation["prefix"] = value.split(":")[0].split(" ")[::-1][0]
            relation["uri"] = value.split(":")[1].split(" ")[0]

            # Cardinality restriction evaluation
            reg_exp = "\(([^)]+)\)"
            max_min_card = re.findall(reg_exp, value)
            max_min_card = max_min_card[0] if len(max_min_card) > 0 else None

            #relation["min_cardinality"] = value.split("(")[-1].split("..")[0]
            #relation["max_cardinality"] = value.split("(")[-1].split("..")[1][:-1]
            relation["min_cardinality"] = max_min_card.split("..")[0] if max_min_card is not None else None
            relation["max_cardinality"] = max_min_card.split("..")[1] if max_min_card is not None else None
            relation["type"] = "owl:ObjectProperty"

            relations.append(relation)

        # Dictionary of Namespaces
        elif "shape=note" in style:
            html_data = html.unescape(value)
            soup = BeautifulSoup(html_data, features="html.parser")
            for div in soup:
                prefix = div.contents[0]
                # Sometimes the prefix can be in bold
                if type(prefix) == bs4.element.Tag:
                    prefix = prefix.contents[0]
                    prefix = prefix.split(":")[0]

                ontology_uri = str(div.contents[1])
                namespaces[prefix] = ontology_uri

        # Dictionary of ontology level metadata
        elif "shape=document" in style:
            html_data = html.unescape(value)
            soup = BeautifulSoup(html_data, features="html.parser")
            for div in soup:
                #ann_type = div.contents[0]
                content = div.contents[0]
                ann_type = str(content).split(":")[0]
                ann_value = str(content).split(":")[1].split(" ")[-1]
                #if type(ann_type) == bs4.element.Tag:
                #    ann_type = ann_type.contents[0]
                #    ann_type = ann_type.split(":")[0]

                #ann_value = str(div.contents[1])
                ontology_metadata[ann_type] = ann_value

        elif "ellipse" in style:
            unnamed = {}
            unnamed["id"] = id
            unnamed["xml_object"] = child
            if "⨅" in value:
                unnamed["type"] = "owl:intersectionOf"
            elif "⨆" in value:
                unnamed["type"] = "owl:unionOf"
            elif "≡" in value:
                unnamed["type"] = "owl:equivalentClass"
            elif "⊥" in value:
                unnamed["type"] = "owl:disjointWith"
            else:
                # If the type is not embedded we have to look for free text in a small neighborhood
                ellipse_geom = child[0]
                x, y, = ellipse_geom["x"], ellipse_geom["y"]
                width, height = ellipse_geom["width"], ellipse_geom["height"]
                ellipse_ctr = (x+(width/2), y+(height/2))
                # Second iteration to find the associated free text to this blank node
                unnamed["type"] = None
                for child2 in root:
                    if "text" in child2["style"]:
                        text_geom = child2[0]
                        x, y = text_geom.attrib["x"], text_geom.attrib["y"]
                        width, height = text_geom.attrib["width"], text_geom.attrib["height"]
                        text_ctr = (x+(width/2), y+(height/2))
                        d = math.sqrt((ellipse_ctr[0] - text_ctr[0])**2 + (ellipse_ctr[1] - text_ctr[1])**2)
                        # This evaluation considers that only one free text element will be on the
                        # surroundings of a ellipse blank node element.
                        if d < 100:
                            if "intersectionOf" in child2.attrib["value"]:
                                unnamed["type"] = "owl:intersectionOf"
                            elif "unionOf" in child2.attrib["value"]:
                                unnamed["type"] = "owl:unionOf"
                            break

            # Find the associated concepts to this union / intersection restriction
            unnamed["group"] = []
            for child2 in root:
                if "edge" in child2.attrib:
                    source_id = child2.attrib["source"]
                    if id == source_id:
                        target_id = child2.attrib["target"]
                        unnamed["group"].append(target_id)

            anonymous_concepts.append(unnamed)

        # List of individuals
        # The "&lt;u&gt;" value indicates "bold" in html
        elif "fontStyle=4" in style or "&lt;u&gt;" in value:
            individual = {}
            individual["id"] = id
            individual["xml_object"] = child
            # The underlining is done at the style level
            if "fontStyle=4" in style:
                individual["prefix"] = value.split(":")[0]
                individual["uri"] = value.split(":")[1]
            # Or at the value level (vaya mierda)
            else:
                individual["prefix"] = value.split(";")[2].split("&")[0].split(":")[0]
                individual["uri"] = value.split(";")[2].split("&")[0].split(":")[1]
            individuals.append(individual)

        else:
            concept = {}
            attribute_block = {}
            attribute_block["id"] = id
            attribute_block["xml_object"] = child

            geometry = child[0]
            x, y = float(geometry.attrib["x"]), float(geometry.attrib["y"])
            width, height = float(geometry.attrib["width"]), float(geometry.attrib["height"])
            p1, p2, p3, p4 = get_corners(x, y, width, height)

            # We need a second iteration because we need to know if there is a block
            # on top of the current block, that determines if we are dealing with a class or attributes
            for child2 in root:
                style2 = child2.attrib["style"]
                value2 = child2.attrib["value"] if "value" in child2.attrib else None
                # Filter all the elements except attributes and classes
                if "edge" not in child2.attrib and "ellipse" not in style2 and "shape" not in style2 and \
                        "fontStyle=4" not in style2 and "&lt;u&gt;" not in value2:

                    geometry = child2[0]

                    x, y = float(geometry.attrib["x"]), float(geometry.attrib["y"])
                    width, height = float(geometry.attrib["width"]), float(geometry.attrib["height"])
                    p1_support, p2_support, p3_support, p4_support = get_corners(x, y, width, height)
                    dx = abs(p1[0] - p2_support[0])
                    dy = abs(p1[1] - p2_support[1])

                    if dx < 5 and dy < 5:
                        attributes = []
                        attribute_list = value.split("<br>")
                        domain = False if "dashed=1" in style else True
                        for attribute_value in attribute_list:
                            attribute = {}
                            attribute["prefix"] = attribute_value.split(":")[0].split(" ")[::-1][0]
                            attribute["uri"] = attribute_value.split(":")[1].split(" ")[0]
                            if len(attribute_value.split(":")) > 2:
                                attribute["datatype"] = attribute_value.split(":")[2][1:].lower()
                            else:
                                attribute["datatype"] = None
                            if attribute["datatype"] is None or attribute["datatype"] == "":
                                attribute["range"] = False
                            else:
                                attribute["range"] = True
                            attribute["domain"] = domain

                            # Existential Universal restriction evaluation
                            if "(all)" in attribute_value or "∀" in attribute_value:
                                attribute["allValuesFrom"] = True
                            else:
                                attribute["allValuesFrom"] = False

                            if "(some)" in attribute_value or "∃" in attribute_value:
                                attribute["someValuesFrom"] = True
                            else:
                                attribute["someValuesFrom"] = False

                            attribute["functional"] = True if "(F)" in attribute_value else False
                            attribute["min_cardinality"] = attribute_value.split("..")[0][-1] \
                                if len(attribute_value.split("..")) > 1 else None
                            attribute["max_cardinality"] = attribute_value.split("..")[1].split(")")[0] \
                                if attribute["min_cardinality"] is not None else None

                            attributes.append(attribute)

                        attribute_block["attributes"] = attributes
                        attribute_block["concept_associated"] = child2.attrib["id"]
                        attribute_blocks.append(attribute_block)
                        attributes_found = True
                        break

            # If after a dense one to all evaluation the object selected cannot be associated
            # to any other object it means that it is a class
            if not attributes_found:
                concept["id"] = id
                concept["prefix"] = value.split(":")[0]
                concept["uri"] = value.split(":")[1]
                concepts.append(concept)

    return concepts, attribute_blocks, relations, individuals, anonymous_concepts, \
           ontology_metadata, namespaces


def concept_attributes_association(concepts, attribute_blocks):

    associations = []

    for concept in concepts:
        associations.append({"concept": concept})

    for attribute_block in attribute_blocks:
        for association in associations:
            if attribute_block["concept_associated"] == association["concept"]["id"]:
                association["attribute_block"] = attribute_block

    return associations

def concept_relations_association(associations, relations):

    #concept_atr_rel_triplets = copy.deepcopy(concept_attribute_pairs)
    for relation in relations:
        source_id = relation["source"]
        target_id = relation["target"]
        for i, association in enumerate(associations):
            concept_id = association["concept"]["id"]
            try:
                attribute_block_id = association["attribute_block"]["id"]
            except:
                attribute_block_id = None
            if concept_id == source_id or attribute_block_id == source_id:
                if "relations" in association:
                    association["relations"].append(relation)
                else:
                    association["relations"] = [relation]
                break
        """
        for j, pair in enumerate(concept_attribute_pairs):
            concept_id = pair["concept"].attrib["id"]
            try:
                attributes_id = pair["attributes"].attrib["id"]
            except:
                attributes_id = None
            if concept_id == target_id or attributes_id == target_id:
                concept_atr_rel_triplets[i]["relations"][-1]["target_concept"] = pair["concept"]
                break
        """
    return associations


def get_ttl_template(filename, onto_uri, onto_prefix):

    file = open(filename, 'w')
    file.write("@prefix " + onto_prefix + ": " + onto_uri + " .\n")
    file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
               "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
               "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
               "@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n"
               "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")

    file.write(onto_uri + " rdf:type owl:Ontology .\n\n")

    return file

tree = ET.parse("data/kpi.xml")
mxfile = tree.getroot()
root = mxfile[0][0][0]

# Eliminate children related to the whole white template
for elem in root:
    if elem.attrib["id"] == "0":
        root.remove(elem)
        break
for elem in root:
    if elem.attrib["id"] == "1":
        root.remove(elem)
        break

filename = "owl_code.ttl"
all_elements = find_elements(root)
concepts, attribute_blocks, relations = all_elements[0:3]
individuals, anonymous_concepts, ontology_metadata, namespaces = all_elements[3:]
onto_prefix = list(namespaces.keys())[0]
onto_uri = namespaces[onto_prefix]


print("Namespaces######################")
print(namespaces)
print("Ontology Metadata ##############")
print(ontology_metadata)
print("Concepts #####################")
for concept in concepts:
    print(concept)
print("Attributes #####################")
for attribute_block in attribute_blocks:
    print(attribute_block)
print("Relations #####################")
for relation in relations:
    print(relation)
print("Individuals ###################")
for individual in individuals:
    print(individual)
print("Unnamed #######################")
for unnamed in anonymous_concepts:
    print(unnamed)

associations = concept_attributes_association(concepts, attribute_blocks)
associations = concept_relations_association(associations, relations)

#pairs = concept_attribute_association(root)
#triplets = concept_relation_association(pairs, relations)


file = get_ttl_template(filename, onto_uri, onto_prefix)

file.write("#################################################################\n"
           "#    Object Properties\n"
           "#################################################################\n\n")


for relation in relations:

    if relation["type"] == "owl:ObjectProperty":
        uri = relation["uri"]
        prefix = relation["prefix"]
        domain = relation["domain"]
        range = relation["range"]
        functional = relation["functional"]

        file.write("### " + prefix + ":" + uri + "\n")
        if functional:
            file.write(prefix + ":" + uri + " rdf:type owl:ObjectProperty ,\n")
            file.write("\t\t\towl:FunctionalProperty .\n\n")
        else:
            file.write(prefix + ":" + uri + " rdf:type owl:ObjectProperty .\n\n")

"""
file.write("#################################################################\n"
           "#    Datatype Properties\n"
           "#################################################################\n\n")

for attributes in attribute_blocks:

    attributes = re.split("<br>", attributes.attrib["value"])
    for attribute in attributes:
        index_prefix = attribute.find(":")
        index_sufix = attribute.find("::")
        cardinality_limit_1 = attribute.find("(")
        cardinality_limit_2 = attribute.find(")")
        cardinality_sep = attribute.find("..")
        max_cardinality = attribute[cardinality_sep+2:cardinality_limit_2]
        attrib_name_without_prefix = attribute[index_prefix + 1:index_sufix]
        attrib_name_with_prefix = attribute[cardinality_limit_2 + 1:index_sufix]
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
    last_upper_case = re.findall("[A-Z]", concept_name_without_prefix)[-1]
    sep_index = concept_name_without_prefix.find(last_upper_case)
    label = concept_name_without_prefix[:sep_index] + " " + concept_name_without_prefix[sep_index:].lower()
    #print(concept_name_with_prefix)
    if len(triplet) > 1:

        if "fontStyle=4" not in concept.attrib["style"]:
            file.write(concept_name_with_prefix + " rdf:type owl:Class ;\n")
            file.write("\trdfs:subClassOf \n")
        if "attributes" in triplet:
            attribute_block = triplet["attributes"]
            attributes = re.split("<br>", attribute_block.attrib["value"])
            for i, attribute in enumerate(attributes):
                index_prefix = attribute.find(":")
                index_sufix = attribute.find("::")
                cardinality_limit_1 = attribute.find("(")
                cardinality_limit_2 = attribute.find(")")
                cardinality_sep = attribute.find("..")
                #max_cardinality = attribute[cardinality_sep + 2:cardinality_limit_2]
                min_cardinality = attribute[cardinality_limit_1+1:cardinality_sep]
                attrib_name_with_prefix = attribute[cardinality_limit_2 + 1:index_sufix]
                attribute_type = attribute[index_sufix+2:][0].lower() + attribute[index_sufix+2:][1:]
                file.write("\t\t[ rdf:type owl:Restriction ;\n"
                           "\t\towl:onProperty {} ;\n".format(attrib_name_with_prefix))
                # Check these rules because I'm not sure if a min cardinality of 0 means
                # an existential restriction of type allValuesFrom, I think not!
                if int(min_cardinality) != 0:
                    file.write("\t\towl:someValuesFrom xsd:{} ]".format(attribute_type))
                else:
                    file.write("\t\towl:allValuesFrom xsd:{} ]".format(attribute_type))
                if i < len(attributes) - 1:
                    file.write(",\n")
                elif i == len(attributes) - 1 and "relations" in triplet:
                    file.write(",\n")
                else:
                    file.write(".\n")

        if "relations" in triplet:
            relations = triplet["relations"]
            for j, relation in enumerate(relations):
                link = relation["link"]
                target_concept = relation["target_concept"]
                target_concept_name = target_concept.attrib["value"]
                if "value" in link.attrib:
                    link_name = link.attrib["value"]
                    cardinality_limit_1 = link_name.find("(")
                    #cardinality_limit_2 = link.attrib["value"].find(")")
                    cardinality_sep = link_name.find("..")
                    min_cardinality = link_name[cardinality_limit_1 + 1:cardinality_sep]
                    relation_name_with_prefix = link_name[:cardinality_limit_1 - 1]
                    file.write("\t\t[ rdf:type owl:Restriction ;\n"
                               "\t\towl:onProperty {} ;\n".format(relation_name_with_prefix))
                    if int(min_cardinality) != 0:
                        file.write("\t\towl:someValuesFrom {} ]".format(target_concept_name))
                    else:
                        file.write("\t\towl:allValuesFrom {} ]".format(target_concept_name))
                else:
                    if "fontStyle=4" in concept.attrib["style"]:
                        file.write(concept_name_with_prefix + " rdf:type " + target_concept_name)
                    else:
                        file.write("\t\t{}".format(target_concept_name))

                if j < len(relations) - 1:
                    file.write(",\n")
                else:
                    file.write(".\n")

    else:
        file.write(concept_name_with_prefix + " rdf:type owl:Class .\n\n")
"""