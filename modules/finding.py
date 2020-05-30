import re
import math
from modules.geometry import get_corners_rect_child
from modules.utils import clean_html_tags


def find_relations(root):

    relations = {}
    for child in root:

        id = child.attrib["id"]
        style = child.attrib["style"]
        value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None
        discard_edge = False

        if "edge" in child.attrib:
            relation = {}
            source = child.attrib["source"] if "source" in child.attrib else None
            target = child.attrib["target"] if "target" in child.attrib else None

            relation["source"] = source
            relation["target"] = target  # (Then Evaluate what happen if they do not have target or source)
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
                    style2 = child2.attrib["style"]
                    if ("text" in style2 or "edgeLabel" in style2) and id == child2.attrib["parent"]:
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
                    relations[id] = relation
                    continue

            if "subClassOf" in value:
                relation["type"] = "rdfs:subClassOf"
                relations[id] = relation
                continue
            if "type" in value:
                relation["type"] = "rdf:type"
                relations[id] = relation
                continue
            if "equivalentClass" in value:
                relation["type"] = "owl:equivalentClass"
                relations[id] = relation
                continue
            if "disjointWith" in value:
                relation["type"] = "owl:disjointWith"
                relations[id] = relation
                continue
            if "subPropertyOf" in value:
                relation["type"] = "owl:subPropertyOf"
                relations[id] = relation
                continue
            if "equivalentProperty" in value:
                relation["type"] = "owl:equivalentProperty"
                relations[id] = relation
                continue
            if "inverseOf" in value:
                relation["type"] = "owl:inverseOf"
                relations[id] = relation
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

            value = clean_html_tags(value)
            # Finding the property uri
            splitted_value = value.split("</div>")
            splitted_value = [item for item in splitted_value if item != ""]
            splitted_value = splitted_value[1:] if "owl" in value else splitted_value
            splitted_value = splitted_value[0]

            prefix = splitted_value.split(":")[0].strip().split(" ")
            prefix = [item for item in prefix if item != ""][-1].strip()

            uri = splitted_value.split(":")[1].strip().split(" ")
            uri = [item for item in uri if item != ""][0].strip()
            relation["prefix"] = prefix
            relation["uri"] = uri

            # Cardinality restriction evaluation
            reg_exp = "\(([0-9][^)]+)\)"
            max_min_card = re.findall(reg_exp, value)
            max_min_card = max_min_card[-1] if len(max_min_card) > 0 else None

            relation["min_cardinality"] = max_min_card.split("..")[0] if max_min_card is not None else None
            if relation["min_cardinality"] == "0":
                relation["min_cardinality"] = None

            relation["max_cardinality"] = max_min_card.split("..")[1] if max_min_card is not None else None
            if relation["max_cardinality"] == "N":
                relation["max_cardinality"] = None

            relation["type"] = "owl:ObjectProperty"

            relations[id] = relation

    return relations


def find_namespaces(root):

    namespaces = {}

    for child in root:

        style = child.attrib["style"]
        value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None

        # Dictionary of Namespaces
        if "shape=note" in style:
            splitted_value = value.split("</div>")
            splitted_value = [item for item in splitted_value if item != ""]
            splitted_value = [subitem for item in splitted_value for subitem in item.split("<br>")]
            splitted_value = [item for item in splitted_value if item != ""]
            splitted_value = [re.sub("&nbsp;", " ", item) for item in splitted_value]
            for item in splitted_value:
                prefix = item.split(":")[0].strip()
                ontology_uri = item.split(":")[1:]
                ontology_uri = [item.strip() for item in ontology_uri]
                ontology_uri = ":".join(ontology_uri).strip()
                namespaces[prefix] = ontology_uri
    return namespaces


def find_metadata(root):

    ontology_metadata = {}

    for child in root:

        style = child.attrib["style"]
        value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None

        # Dictionary of ontology level metadata
        if "shape=document" in style:
            splitted_value = value.split("</div>")
            splitted_value = [item for item in splitted_value if item != ""]
            splitted_value = [subitem for item in splitted_value for subitem in item.split("<br>")]
            splitted_value = [item for item in splitted_value if item != ""]
            splitted_value = [re.sub("&nbsp;", " ", item) for item in splitted_value]
            for item in splitted_value:
                ann_type = item.split(":")[0].strip()
                ann_value = item.split(":")[1].strip()
                ontology_metadata[ann_type] = ann_value

    return ontology_metadata


def find_ellipses(root):

    ellipses = {}

    for child in root:

        id = child.attrib["id"]
        style = child.attrib["style"]
        value = child.attrib["value"] if "value" in child.attrib else None

        if "ellipse" in style:
            ellipse = {}
            ellipse["xml_object"] = child
            if "⨅" in value:
                ellipse["type"] = "owl:intersectionOf"
            elif "⨆" in value:
                ellipse["type"] = "owl:unionOf"
            elif "≡" in value:
                ellipse["type"] = "owl:equivalentClass"
            elif "⊥" in value:
                ellipse["type"] = "owl:disjointWith"
            else:
                # If the type is not embedded we have to look for free text in a small neighborhood
                ellipse_geom = child[0]
                x, y = float(ellipse_geom.attrib["x"]), float(ellipse_geom.attrib["y"])
                width, height = float(ellipse_geom.attrib["width"]), float(ellipse_geom.attrib["height"])
                ellipse_ctr = (x+(width/2), y+(height/2))
                # Second iteration to find the associated free text to this blank node
                ellipse["type"] = None
                for child2 in root:
                    if "text" in child2.attrib["style"]:
                        text_geom = child2[0]
                        x, y = float(text_geom.attrib["x"]), float(text_geom.attrib["y"])
                        width, height = float(text_geom.attrib["width"]), float(text_geom.attrib["height"])
                        text_ctr = (x+(width/2), y+(height/2))
                        d = math.sqrt((ellipse_ctr[0] - text_ctr[0])**2 + (ellipse_ctr[1] - text_ctr[1])**2)
                        # This evaluation considers that only one free text element will be on the
                        # surroundings of a ellipse blank node element.
                        if d < 100:
                            if "intersectionOf" in child2.attrib["value"]:
                                ellipse["type"] = "owl:intersectionOf"
                            elif "unionOf" in child2.attrib["value"]:
                                ellipse["type"] = "owl:unionOf"
                            break

            # Find the associated concepts to this union / intersection restriction
            ellipse["group"] = []
            for child2 in root:
                if "edge" in child2.attrib:
                    source_id = child2.attrib["source"]
                    if id == source_id:
                        target_id = child2.attrib["target"]
                        ellipse["group"].append(target_id)

            ellipses[id] = ellipse

    return ellipses


def find_individuals(root):

    individuals = {}

    for child in root:

        id = child.attrib["id"]
        style = child.attrib["style"]

        if "value" in child.attrib:
            value = child.attrib["value"]
        else:
            continue

        # List of individuals
        if "fontStyle=4" in style or "<u>" in value:
            individual = {}
            individual["xml_object"] = child
            # The underlining is done at the style level
            if "fontStyle=4" in style:
                individual["prefix"] = value.split(":")[0]
                individual["uri"] = value.split(":")[1]
            else:
                individual["prefix"] = value[3:-4].split(":")[0]
                individual["uri"] = value[3:-4].split(":")[1]
            individual["type"] = None
            individuals[id] = individual

    return individuals


def find_attribute_values(root):

    attributes = {}

    for child in root:
        id = child.attrib["id"]

        if "value" in child.attrib:
            value = child.attrib["value"]
        else:
            continue

        if "&quot;" in value or "\"" in value:
            attribute = {}
            attribute["xml_object"] = child
            attribute["type"] = None

            # Finding the value
            if "&quot;" in value:
                attribute["value"] = value.split("&quot;")[1]
            elif "\"" in value:
                reg_exp = '"(.*?)"'
                attribute["value"] = re.findall(reg_exp, value)[0]

            # Finding the type
            if "^^" in value:
                attribute["type"] = value.split("^^")[-1]

            attributes[id] = attribute

    return attributes


def find_concepts_and_attributes(root):

    concepts = {}
    attribute_blocks = {}

    for child in root:

        id = child.attrib["id"]
        style = child.attrib["style"]
        value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None
        attributes_found = False

        # Check that neither of these components passes, this is because concepts
        # and attributes shape do not have a specific characteristic to differentiate them
        # and we have to use the characteristics of the rest of the shapes
        if "text" in child.attrib["style"]:
            continue
        if "edge" in child.attrib:
            continue
        if "ellipse" in style:
            continue
        if "shape" in style:
            continue
        if "fontStyle=4" in style or "<u>" in value:
            continue
        if "&quot;" in value or "\"" in value:
            continue

        concept = {}
        attribute_block = {}
        attribute_block["xml_object"] = child

        p1, p2, p3, p4 = get_corners_rect_child(child)

        # We need a second iteration because we need to know if there is a block
        # on top of the current block, that determines if we are dealing with a class or attributes
        for child2 in root:
            style2 = child2.attrib["style"]
            # Filter all the elements except attributes and classes
            if "text" in child2.attrib["style"]:
                continue
            if "edge" in child2.attrib:
                continue
            if "ellipse" in style2:
                continue
            if "shape" in style2:
                continue

            p1_support, p2_support, p3_support, p4_support = get_corners_rect_child(child2)
            dx = abs(p1[0] - p2_support[0])
            dy = abs(p1[1] - p2_support[1])

            if dx < 5 and dy < 5:
                attributes = []

                attribute_list = value.split("</div>")
                attribute_list = [item for item in attribute_list if item != ""]
                attribute_list = [subitem for item in attribute_list for subitem in item.split("<br>")]
                attribute_list = [item for item in attribute_list if item != ""]
                attribute_list = [re.sub("&nbsp;", " ", item) for item in attribute_list]

                domain = False if "dashed=1" in style else True
                for attribute_value in attribute_list:
                    attribute = {}
                    attribute["prefix"] = attribute_value.split(":")[0].split(" ")[::-1][0]
                    attribute["uri"] = attribute_value.split(":")[1].split(" ")[0]
                    if len(attribute_value.split(":")) > 2:
                        attribute["datatype"] = attribute_value.split(":")[2][1:].lower().strip()
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

                    if attribute["min_cardinality"] == "0":
                        attribute["min_cardinality"] = None

                    attribute["max_cardinality"] = attribute_value.split("..")[1].split(")")[0] \
                        if len(attribute_value.split("..")) > 1 else None

                    if attribute["max_cardinality"] == "N":
                        attribute["max_cardinality"] = None

                    attributes.append(attribute)

                attribute_block["attributes"] = attributes
                attribute_block["concept_associated"] = child2.attrib["id"]
                attribute_blocks[id] = attribute_block
                attributes_found = True
                break

        # If after a dense one to all evaluation the object selected cannot be associated
        # to any other object it means that it is a class
        if not attributes_found:
            concept["prefix"] = value.split(":")[0]
            concept["uri"] = value.split(":")[-1]
            concept["xml_object"] = child
            concepts[id] = concept

    return concepts, attribute_blocks


def find_elements(root):

    namespaces = find_namespaces(root)
    metadata = find_metadata(root)
    relations = find_relations(root)
    ellipses = find_ellipses(root)
    individuals = find_individuals(root)
    concepts, attribute_blocks = find_concepts_and_attributes(root)

    return concepts, attribute_blocks, relations, individuals, ellipses, metadata, namespaces
