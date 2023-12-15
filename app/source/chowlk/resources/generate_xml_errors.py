import xml.etree.ElementTree as ET
import base64
from urllib.parse import unquote
import zlib

# Default parent
parent = '1'

# This function generate an xml file which indicates the errors in the diagram.
# For each error, the element involved is marked in red and a card is generated describing the error.
def generate_xml_error(diagram_path, errors, path):

    # Load the diagram
    mxfile, root = load_xml(diagram_path)

    # Find the parent (element which represents the background of the diagram)
    global parent
    parent = root[0].attrib['id']

    diagram_modified = False
    error_num = 0

    # Iterate the errors detected in the diagram
    for error_type, error in errors.items():

        # Is the error a list? (i.e. more than one error of the same type)
        if isinstance(error, list):

            # Iterate the errors with the same type
            for content in error:

                # Is the error related to an element? (i.e. the identifier of the element has been stored)
                if 'shape_id' in content and 'message' in content:
                    diagram_modified = True
                    # Find the related element
                    elem = root.find(".//*[@id='"+content['shape_id']+"']")
                    # Find the position of the element in the diagram
                    x,y = find_x_y(root, elem)
                    # Create a card to indicate the error
                    card = create_card(x, y, content['shape_id'], content['message'], error_num)
                    root.append(card)
                    # Change the color of the element
                    mark_element(elem)
                    error_num = error_num + 1               

        else:

            # Is the error related to an element? (i.e. the identifier of the element has been stored)
            if 'shape_id' in error:
                diagram_modified = True
                # Find the related element
                elem = root.find(".//*[@id='"+error['shape_id']+"']")
                # Change the color of the element
                mark_element(elem)
                error_num = error_num + 1
    
    return ET.tostring(mxfile, encoding='unicode', method='xml'), diagram_modified

# This function has to load (again) the xml diagram for two reasons:
# 1) The diagram loaded in order to generate the ontology has been modified (the old root has become useless).
# 2) If the xml file is compressed, it is needed to add the header tags to the decompressed diagram
def load_xml(diagram_path):
    tree = ET.parse(diagram_path)
    mxfile = tree.getroot()

    try:
        # Check if the diagram is decompressed
        # If the diagram is decompressed the tag structure is like the following:
        # <mxfile> <diagram> <mxGraphModel> <root> ...
        diagram = mxfile[0]
        mxGraphModel = diagram[0]
        root = mxGraphModel[0]

    except:
        # The diagram is compressed
        # If the diagram is compressed the tag structure is like the following:
        # <mxfile> <diagram> compress_diagram ...
        diagram = mxfile[0]
        compressed_mxGraphModel = diagram.text

        # Decompress the diagram. The tag structure of xml_string is like the following:
        # <mxGraphModel> <root> ...
        # It is neccesary to add the <mxfile> and <diagram> tags
        coded_xml = base64.b64decode(compressed_mxGraphModel)
        xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))

        # Add the <diagram> tag
        xml_string = ">" + xml_string + "</diagram>"
        for key, value in diagram.items():
            xml_string = key + '="' + value +'" ' + xml_string
        xml_string = "<diagram " + xml_string

        # Add the <mxfile> tag
        xml_string = ">" + xml_string + "</mxfile>"
        for key, value in mxfile.items():
            xml_string = key + '="' + value +'" ' + xml_string
        xml_string = "<mxfile " + xml_string

        # Convert the string to a tree
        tree = ET.ElementTree(ET.fromstring(xml_string))
        mxfile = tree.getroot()
        diagram = mxfile[0]
        mxGraphModel = diagram[0]
        root = mxGraphModel[0]

    return mxfile, root

# This function mark in red the element which is involved in an error
def mark_element(elem):
    style = elem.attrib['style']
    start_index = style.rfind('strokeColor=')

    # Does the element have a colour defined?
    if start_index != -1:
        # Change the colour of the element to red
        end_index = style.find(';', start_index)
        style = style[:start_index] + 'strokeColor=#FF3333' + style[end_index:]
    else:
        # Colour the element in red
        style = style + 'strokeColor=#FF3333;'
    elem.attrib['style'] = style

# Find the position of the element associated to the error
def find_x_y(root, elem):

    # Is the element an arrow?
    if "edge" in elem.attrib:

        # If the arrow is connected to another element (i.e. has a target or a source), the arrow has no coordinates.
        # In this case, the coordinates are taken from the elements to which it is connected.
        # Otherwise, the arrow must to have coordinates.
        target_source_id = elem.attrib["target"] if "target" in elem.attrib else elem.attrib["source"] if "source" in elem.attrib else ""
        
        # Is the arrow connected to another element?
        if target_source_id!="":
            try:
                # Find the element to which the arrow is connected
                target_source = root.find(".//*[@id='"+target_source_id+"']")
                # Obtain the coordinates of the element to which the arrow is connected
                x,y = find_x_y(root, target_source)
            except:
                # The diagram is corrupted because the identifier "target_source_id" is not defined
                x = "0"
                y = "0"

        else:
            # If the arrow is not connected to another element, it should has coordinates
            # Does the arrow store coordinates?
            if len(elem) > 0 and len(elem[0]) > 0:
                mxpoint = elem[0][0]
                x = mxpoint.attrib['x'] if 'x' in mxpoint.attrib else "0"
                y = mxpoint.attrib['y'] if 'y' in mxpoint.attrib else "0"
            else:
                # The arrow has not coordinates associated (this should not happen)
                x = "0"
                y = "0"
        
    else:
        # The element is not an arrow.
        # The coordinates should be stored in the same element.
        # Sometimes the coordinates are stored in another element whose identifier is stored in the attribute parent.
        mxgeometry = elem[0]

        # Are the coordinates stored in the element?
        if 'x' in mxgeometry.attrib and 'y' in mxgeometry.attrib:
            x = mxgeometry.attrib['x']
            y = mxgeometry.attrib['y']

        else:
            elem_parent_id = elem.attrib['parent']
            
            # Has the element a parent in which the coordinates are stored?
            if elem_parent_id != parent:

                try:
                    # Find the parent element
                    elem_parent = root.find(".//*[@id='"+elem_parent_id+"']")
                    # Obtain the coordinates of the parent element
                    x,y = find_x_y(root, elem_parent)

                except:
                    # The diagram is corrupted because the identifier "elem_parent_id" is not defined
                    x = "0"
                    y = "0"

            else:
                # The element has not coordinates associated (this should not happen)
                x = "0"
                y = "0"

    return x,y

# Create a card whose coordinates are the same as the element and contains the error description.
# The identifier of the card is (id of the element which has an error)-card-(number of the card generated)
def create_card(x, y, id, message, error_num):

    # Create the card
    mxCell = ET.Element('mxCell')
    mxCell.set("id", id + "-card-" + str(error_num))
    mxCell.set("value", message)
    mxCell.set("style", "shape=card;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;")
    mxCell.set("parent", parent)
    mxCell.set("vertex", "1")
    
    # Create the position of the card
    mxGeometry = ET.SubElement(mxCell, 'mxGeometry')
    mxGeometry.set("x", x)
    mxGeometry.set("y", y)
    mxGeometry.set("width", "80")
    mxGeometry.set("height", "100")
    mxGeometry.set("as", "geometry")

    return mxCell
    