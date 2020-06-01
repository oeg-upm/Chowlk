import xml.etree.ElementTree as ET
from modules.geometry import proximity_to_shape
import re
import copy

def create_label(uri, type):

    uppers_pos = [uri.index(char) for char in uri if char.isupper()]
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
    reg_exp = "(<span .[^>]+\>)"

    for tag in html_tags:
        if tag in value:
            value = re.sub(tag, "", value)

    if "span" in value:
        value = re.sub(reg_exp, "", value)

    if "&lt;" in value:
        value = re.sub("&lt;", "<", value)

    if "&gt;" in value:
        value = re.sub("&gt;", ">", value)

    return value


def read_drawio_xml(diagram_path):

    tree = ET.parse(diagram_path)
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

    return root


def fix_source_target(relations, shapes_list):

    shapes = {shape_id: shape for shapes in shapes_list for shape_id, shape in shapes.items()}
    relations_copy = copy.deepcopy(relations)

    for id, relation in relations.items():

        source = relation["source"]
        target = relation["target"]
        for side in [source, target]:

            if side is None:
                xml_object = relation["xml_object"]
                mxpoint_object = xml_object[0][0]
                mxpoint_x = float(mxpoint_object.attrib["x"])
                mxpoint_y = float(mxpoint_object.attrib["y"])
                mxpoint_side = mxpoint_object.attrib["as"].split("Point")[0]

                for shape_id, shape in shapes.items():
                    xml_shape = shape["xml_object"]
                    proximity = proximity_to_shape((mxpoint_x, mxpoint_y), xml_shape, thr=10)
                    if proximity:
                        relations_copy[id][mxpoint_side] = shape_id
                        break

                if relations_copy[id][mxpoint_side] is None:
                    raise ValueError("The " + mxpoint_side + " side of relation " + relation["prefix"] +
                                     ":" + relation["uri"] + " is not connected or even close to any shape, verify it")

    return relations_copy










