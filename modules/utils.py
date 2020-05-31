import xml.etree.ElementTree as ET
import os
import re

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
