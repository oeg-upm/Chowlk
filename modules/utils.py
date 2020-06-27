import xml.etree.ElementTree as ET
from modules.geometry import proximity_to_shape
import re
import copy
import base64
from urllib.parse import unquote
import zlib

def create_label(uri, type):

    uppers_pos = []
    for i, char in enumerate(uri):
        if char.isupper():
            uppers_pos.append(i)
    uppers_pos.insert(0, 0) if 0 not in uppers_pos else uppers_pos
    words = []
    
    for i, current_pos in enumerate(uppers_pos):
        
        if i+1 < len(uppers_pos):
            next_pos = uppers_pos[i + 1]
            word = uri[current_pos:next_pos]
        else:
            word = uri[current_pos:]

        word = word.lower() if type == "property" else word
        words.append(word)

    label = " ".join(words)

    return label


def clean_html_tags(value):

    """
    Function to clean some noisy html tags on the names of the concepts,
    properties and other elements. Just the </div> and <br> tags are left for
    later use in order to identify multiple attributes in the same attribute block
    :param value: value attribute of a child, string
    :return: return the same value cleaned.
    """

    html_tags = ["<div>", "<b>", "</b>", "</span>"]
    span_reg_exp = "(<span .[^>]+\>)"
    div_reg_exp = "(<div .[^>]+\>)"

    for tag in html_tags:
        if tag in value:
            value = re.sub(tag, "", value)

    if "span" in value:
        value = re.sub(span_reg_exp, "", value)

    if "div" in value:
        value = re.sub(div_reg_exp, "", value)

    if "&lt;" in value:
        value = re.sub("&lt;", "<", value)

    if "&gt;" in value:
        value = re.sub("&gt;", ">", value)

    return value


def read_drawio_xml(diagram_path):

    tree = ET.parse(diagram_path)
    mxfile = tree.getroot()

    try:
        root = mxfile[0][0][0]
    except:
        # This lines are for compressed XML files
        compressed_xml = mxfile[0].text
        coded_xml = base64.b64decode(compressed_xml)
        xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))
        root = ET.fromstring(xml_string)[0]

    # Eliminate children related to the whole white template
    for elem in root:
        if elem.attrib["id"] == "0":
            root.remove(elem)
            break
    for elem in root:
        if elem.attrib["id"] == "1":
            root.remove(elem)
            break

    return root


def swap_source_target(relation):

    xml_object = relation["xml_object"]
    swapped = detect_source_target_swapped(xml_object)
    init_source = relation["source"]
    init_target = relation["target"]

    if swapped == True:
        relation["source"] = init_target
        relation["target"] = init_source

    return relation


def detect_source_target_swapped(xml_object):

    style = xml_object.attrib["style"]

    if "startArrow" not in style or "startArrow=none" in style or "startArrow=oval" in style:
        swapped = False
    elif "endArrow=none" not in style:
        swapped = False
    else:
        swapped = True

    return swapped


def fix_source_target(relations, shapes_list):

    shapes = {shape_id: shape for shapes in shapes_list for shape_id, shape in shapes.items()}
    relations_copy = copy.deepcopy(relations)

    for id, relation in relations.items():
        source = relation["source"]
        target = relation["target"]
        xml_object = relation["xml_object"]
        for side in [("source", source), ("target", target)]:
            side_key = side[0]
            side_value = side[1]
            if side_value is None:
                mxgeometry = xml_object[0]
                for mxpoint in mxgeometry:
                    #mxpoint_object = xml_object[0][0]
                    mxpoint_side = mxpoint.attrib["as"].split("Point")[0]
                    if mxpoint_side == side_key:
                        mxpoint_x = float(mxpoint.attrib["x"])
                        mxpoint_y = float(mxpoint.attrib["y"])
                        break
                for shape_id, shape in shapes.items():
                    xml_shape = shape["xml_object"]
                    proximity = proximity_to_shape((mxpoint_x, mxpoint_y), xml_shape, thr=10)
                    if proximity:
                        relations_copy[id][mxpoint_side] = shape_id
                        break
                if relations_copy[id][mxpoint_side] is None:
                    try:
                        raise ValueError("The " + mxpoint_side + " side of relation " + relation["prefix"] + ":" +
                                         relation["uri"] + " is not connected or even close to any shape, verify it!")
                    except:
                        raise ValueError("The " + mxpoint_side + " side of a relation of type " + relation["type"] +
                                         " and id " + id + " is not connected or even close to any shape, "
                                         "verify it!")

        relations_copy[id] = swap_source_target(relations_copy[id])

    return relations_copy


def find_prefixes(concepts, relations, attribute_blocks, individuals):

    prefixes = []

    for id, concept in concepts.items():
        prefix = concept["prefix"]
        if prefix not in prefixes:
            prefixes.append(prefix)

    for id, relation in relations.items():
        if "prefix" in relation:
            prefix = relation["prefix"]
            if prefix not in prefixes:
                prefixes.append(prefix)

    for id, individual in individuals.items():
        prefix = individual["prefix"]
        if prefix not in prefixes:
            prefixes.append(prefix)

    for id, attribute_block in attribute_blocks.items():
        attributes = attribute_block["attributes"]
        for attribute in attributes:
            prefix = attribute["prefix"]
            if prefix not in prefixes:
                prefixes.append(prefix)

    return prefixes





