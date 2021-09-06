import xml.etree.ElementTree as ET
import re
import base64
from urllib.parse import unquote
import zlib
from bs4 import BeautifulSoup

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


def clean_html_tags(text, metadata=False):

    html_tags = ["<u>", "</u>", "<b>", "</b>", "(<span .[^>]+\>)", "(<font .[^>]+\>)", "</font>", "<span>", "</span>"]

    for tag in html_tags:
        text = re.sub(tag, "", text)

    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text("|")
    return text


def read_drawio_xml(diagram_path):

    tree = ET.parse(diagram_path)
    mxfile = tree.getroot()

    try:
        diagram = mxfile[0]
        mxGraphModel = diagram[0]
        root = mxGraphModel[0]
    except:
        # This lines are for compressed XML files
        diagram = mxfile[0]
        compressed_mxGraphModel = diagram.text
        coded_xml = base64.b64decode(compressed_mxGraphModel)
        xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))
        mxGraphModel = ET.fromstring(xml_string)
        root = mxGraphModel[0]

    # Eliminate children related to the whole white template
    for elem in root:
        if elem.attrib["id"][-1] == "0":
            root.remove(elem)
            break
    for elem in root:
        if elem.attrib["id"][-1] == "1":
            root.remove(elem)
            break

    return root


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

def clean_uri(uri):

    uri = re.sub("\(([0-9][^)]+)\)", "", uri).strip()
    uri = re.sub("\(([^)]+)\)", "", uri).strip()
    uri = re.sub("\(all\)", "", uri).strip()
    uri = re.sub("\(some\)", "", uri).strip()
    uri = re.sub("\(∀\)", "", uri).strip()
    uri = re.sub("\(∃\)", "", uri).strip()
    uri = re.sub("\(F\)", "", uri).strip()
    uri = re.sub("\(IF\)", "", uri).strip()
    uri = re.sub("\(S\)", "", uri).strip()
    uri = re.sub("\(T\)", "", uri).strip()

    return uri
