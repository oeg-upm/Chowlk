import xml.etree.ElementTree as ET
import os
import re

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
