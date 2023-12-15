import xml.etree.ElementTree as ET
import re
import base64
from urllib.parse import unquote
import zlib
from bs4 import BeautifulSoup

# The prefix '' means that the user is using base directive 
# (i.e. the user has declared "suffix" for that element).
# The prefix ':' means that the user is using the empty prefix
# (i.e. the user has declared ":suffix" for that element)
# Another prefix means that the user has declared "prefix:suffix", and in this case
# it is neccesary to write the ':' between the prefix and suffix
def base_directive_prefix(prefix):
    if prefix and prefix != ':':
        prefix += ':'
    return prefix

def create_label(prefix, suffix, type):

    if not prefix and suffix[0] == '<' and suffix[-1] == '>':
        suffix = get_suffix(suffix)

    uppers_pos = []
    for i, char in enumerate(suffix):
        if char.isupper():
            uppers_pos.append(i)
    uppers_pos.insert(0, 0) if 0 not in uppers_pos else uppers_pos
    words = []
    
    for i, current_pos in enumerate(uppers_pos):
        
        if i+1 < len(uppers_pos):
            next_pos = uppers_pos[i + 1]
            word = suffix[current_pos:next_pos]
        else:
            word = suffix[current_pos:]

        word = word.lower() if type == "property" else word
        words.append(word)

    label = " ".join(words)

    return label

# In the case of an element which is defined directly by an uri (i.e, is defined as <uri>)
# it is neccesary to obtain just the name of the element in order to create the rdfs:label.
# There are two cases:
#   1) <uri#Name> or <uri/Name> => label is Name
#   2) <uriName> => no label
def get_suffix(suffix):
    cut = max(suffix.rfind('/'), suffix.rfind('#'))
    if cut > 0:
        suffix[(cut+1):-1]
        
    return suffix[(cut+1):-1] if cut > 0 else suffix

# Function to remove the tags used in the xml file
def clean_html_tags(text):

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

# In order to implement @base directive
# If value contains ':' && value does not start with ':' => normal prefix
# If value starts with ':' empty prefix
# If value does not contain ':' => base directive
# If value start with < and finish with > => the user has defined the uri
def parse_prefix_uri(value):
    prefix, uri = '', ''
    value = value.strip()
    
    # Check if it is an uri
    if value[0] == '<' and value[-1] == '>':
        #Check if the uri has an identifier defined (it not finish with / or #)
        if value[-2] == '/' or value[-2] == '#':
            return prefix, uri
        #Check if the uri has an identifier defined (it contains / or #)
        elif '#' not in value and '/' not in value:
            return prefix, uri
        
        uri = value

    elif ':' in value:
        #Empty prefix (:uri)
        if ':' == value[0]:
            prefix = ':'
            uri = value[1:]

        #prefix:uri
        else:
            value_split = value.split(':')
            prefix = value_split[0]
            uri = value_split[1]

    # Base directive
    else:
        uri = f'<#{value}>'

    #Remove spaces
    prefix = re.sub(" ", "", prefix)
    uri = re.sub(" ", "", uri)

    return prefix, uri