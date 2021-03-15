import re
import math
from modules.geometry import get_corners_rect_child
from modules.utils import clean_html_tags
from modules.utils import create_label

class Finder():

    def __init__(self, root):

        self.root = root
        self.relations = {}
        self.namespaces = {}
        self.ontology_metadata = {}
        self.ellipses = {}
        self.individuals = {}
        self.attributes = {}
        self.concepts = {}
        self.attribute_blocks = {}
        self.rhombuses = {}

    def find_relations(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None
            ellipse_connection_detected = False

            if "edge" in child.attrib:
                relation = {}
                source = child.attrib["source"] if "source" in child.attrib else None
                target = child.attrib["target"] if "target" in child.attrib else None

                relation["source"] = source
                relation["target"] = target
                relation["xml_object"] = child

                if value == "" or value is None:

                    # Looking for ellipses in a second iteration
                    for child2 in self.root:
                        style2 = child2.attrib["style"] if "style" in child2.attrib else ""
                        if source == child2.attrib["id"] and "ellipse" in style2:
                            # This edge is part of a unionOf / intersectionOf construct
                            # it is not useful beyond that construction
                            relation["type"] = "ellipse_connection"
                            ellipse_connection_detected = True
                            break
                    if ellipse_connection_detected:
                        self.relations[id] = relation
                        continue

                    # Sometimes edges have their value not embedded into the edge itself, at least not in the
                    # "value" parameter of the object. We can track their associated value by looking for free text
                    # and evaluating the "parent" parameter which will point to an edge.
                    for child2 in self.root:
                        style2 = child2.attrib["style"] if "style" in child2.attrib else ""
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
                        self.relations[id] = relation
                        continue

                if "subClassOf" in value:
                    relation["type"] = "rdfs:subClassOf"
                    self.relations[id] = relation
                    continue
                if "type" in value:
                    relation["type"] = "rdf:type"
                    self.relations[id] = relation
                    continue
                if "equivalentClass" in value:
                    relation["type"] = "owl:equivalentClass"
                    self.relations[id] = relation
                    continue
                if "disjointWith" in value:
                    relation["type"] = "owl:disjointWith"
                    self.relations[id] = relation
                    continue
                if "subPropertyOf" in value:
                    relation["type"] = "rdfs:subPropertyOf"
                    self.relations[id] = relation
                    continue
                if "equivalentProperty" in value:
                    relation["type"] = "owl:equivalentProperty"
                    self.relations[id] = relation
                    continue
                if "inverseOf" in value:
                    relation["type"] = "owl:inverseOf"
                    self.relations[id] = relation
                    continue
                if "domain" in value:
                    relation["type"] = "rdfs:domain"
                    self.relations[id] = relation
                    continue
                if "range" in value:
                    relation["type"] = "rdfs:range"
                    self.relations[id] = relation
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
                #value = clean_html_tags(value)
                if ">>" in value or "<<" in value:
                    continue
                #splitted_value = value.split("</div>")
                #splitted_value = [item for item in splitted_value if item != ""]
                #if len(splitted_value) == 0:
                #    continue
                #splitted_value = splitted_value[1:] if "owl" in value else splitted_value
                #splitted_value = splitted_value[0]
                #prefix = splitted_value.split(":")[0].strip().split(" ")
                #prefix = [item for item in prefix if item != ""][-1].strip()
                #uri = splitted_value.split(":")[-1].strip().split(" ")
                #uri = [item for item in uri if item != ""][0].strip()

                # Cardinality restriction evaluation
                max_min_card = re.findall("\(([0-9][^)]+)\)", value)
                max_min_card = max_min_card[-1] if len(max_min_card) > 0 else None

                uri = re.sub("\(([0-9][^)]+)\)", "", uri).strip()

                prefix = uri.split(":")[0].strip()
                uri = uri.split(":")[-1].strip()
                
                relation["prefix"] = prefix
                relation["uri"] = uri
                relation["label"] = create_label(relation["uri"], "property")

                print(max_min_card)
                print(uri)
                print(value)

                #if max_min_card is not None:
                #    if "<font>" in max_min_card:
                #        max_min_card = max_min_card.split("<font>")
                #        max_min_card = "".join(max_min_card)
                #    if "</font>" in max_min_card:
                #        max_min_card = max_min_card.split("</font>")
                #        max_min_card = "".join(max_min_card)

                if max_min_card is None:
                    relation["min_cardinality"] = None
                    relation["max_cardinality"] = None
                else:
                    max_min_card = max_min_card.split("..")
                    relation["min_cardinality"] = max_min_card[0]
                    relation["max_cardinality"] = max_min_card[1]

                if relation["min_cardinality"] == "0":
                    relation["min_cardinality"] = None

                if relation["max_cardinality"] == "N":
                    relation["max_cardinality"] = None

                relation["type"] = "owl:ObjectProperty"
                
                self.relations[id] = relation

            if "rhombus" in style:
                
                relation = {}
                relation["source"] = None
                relation["target"] = None
                relation["xml_object"] = child

                type = value.split(">>")[0].split("<<")[-1].strip()

                value = value.split("</div>")
                value = [item for item in value if item != ""]
                value = [subitem for item in value for subitem in item.split("<br>")]
                value = [item for item in value if item != ""]
                value = [re.sub("&nbsp;", " ", item) for item in value]

                # The value can be in one line or in two lines
                #value = value[0].split(" ")[1] if len(value) == 1 else value[1]
                value = value[-1].split(">>")[-1].strip()

                relation["prefix"] = value.split(":")[0].strip()
                relation["uri"] = value.split(":")[1].strip()
                relation["label"] = create_label(relation["uri"], "property")

                relation["type"] = type

                relation["domain"] = False
                relation["range"] = False

                relation["allValuesFrom"] = False
                relation["someValuesFrom"] = False

                # Property restriction evaluation
                relation["functional"] = False
                relation["inverse_functional"] = False
                relation["transitive"] = False
                relation["symmetric"] = False

                self.relations[id] = relation
        
        return self.relations


    def find_namespaces(self):

        for child in self.root:

            style = child.attrib["style"] if "style" in child.attrib else ""
            value = child.attrib["value"]
            #value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None

            # Dictionary of Namespaces
            if "shape=note" in style:
                splitted_value = value.split("</div>")
                splitted_value = [item for item in splitted_value if item != ""]
                splitted_value = [subitem for item in splitted_value for subitem in item.split("<br>")]
                splitted_value = [item for item in splitted_value if item != ""]
                splitted_value = [re.sub("&nbsp;", " ", item) for item in splitted_value]
                for item in splitted_value:
                    item = clean_html_tags(item)
                    prefix = item.split(":")[0].strip()
                    ontology_uri = item.split(":")[1:]
                    ontology_uri = [item.strip() for item in ontology_uri]
                    ontology_uri = ":".join(ontology_uri).strip()
                    ontology_uri = clean_html_tags(ontology_uri)
                    self.namespaces[prefix] = ontology_uri
        return self.namespaces


    def find_metadata(self):

        for child in self.root:

            style = child.attrib["style"] if "style" in child.attrib else ""
            value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None

            # Dictionary of ontology level metadata
            if "shape=document" in style:
                splitted_value = value.split("</div>")
                splitted_value = [item for item in splitted_value if item != ""]
                splitted_value = [subitem for item in splitted_value for subitem in item.split("<br>")]
                splitted_value = [item for item in splitted_value if item != ""]
                splitted_value = [re.sub("&nbsp;", " ", item) for item in splitted_value]
                for item in splitted_value:
                    ann_prefix = item.split(":")[0].strip()
                    ann_type = item.split(":")[1].strip()
                    ann_value = item.split(":")[2].strip()
                    if ann_prefix + ":" + ann_type in self.ontology_metadata:
                        self.ontology_metadata[ann_prefix + ":" + ann_type].append(ann_value)
                    else:
                        self.ontology_metadata[ann_prefix + ":" + ann_type] = [ann_value]

        return self.ontology_metadata


    def find_ellipses(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
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
                    for child2 in self.root:
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

                for relation_id, relation in self.relations.items():
                    if relation["type"] == "ellipse_connection":
                        source_id = relation["source"]
                        if id == source_id:
                            target_id = relation["target"]
                            ellipse["group"].append(target_id)

                """
                for child2 in self.root:
                    if "edge" in child2.attrib:
                        print(child2.attrib["id"])
                        source_id = child2.attrib["source"]
                        if id == source_id:
                            target_id = child2.attrib["target"]
                            ellipse["group"].append(target_id)
                """
                ellipse["xml_object"] = child
                self.ellipses[id] = ellipse

        return self.ellipses


    def find_individuals(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""

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
                self.individuals[id] = individual

        return self.individuals


    def find_attribute_values(self):

        for child in self.root:

            id = child.attrib["id"]

            value = child.attrib["value"] if "value" in child.attrib else None

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

                self.attributes[id] = attribute

        return self.attributes

    def find_rhombuses(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else None

            if "rhombus" in style:

                rhombus = {}
                rhombus["xml_object"] = child
                type = value.split(">>")[0].split("<<")[-1].strip()
                rhombus["type"] = type

                value = value.split("</div>")
                value = [item for item in value if item != ""]
                value = [subitem for item in value for subitem in item.split("<br>")]
                value = [item for item in value if item != ""]
                value = [re.sub("&nbsp;", " ", item) for item in value]

                # The value can be in one line or in two lines
                #value = value[0].split(" ")[1] if len(value) == 1 else value[1]
                value = value[-1].split(">>")[-1].strip()
                print(value)
                rhombus["prefix"] = value.split(":")[0].strip()
                rhombus["uri"] = value.split(":")[1].strip()

                self.rhombuses[id] = rhombus

        return self.rhombuses


    def find_concepts_and_attributes(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = clean_html_tags(child.attrib["value"]) if "value" in child.attrib else ""
            attributes_found = False

            # Check that neither of these components passes, this is because concepts
            # and attributes shape do not have a specific characteristic to differentiate them
            # and we have to use the characteristics of the rest of the shapes
            if "text" in style or "edgeLabel" in style:
                continue
            if "edge" in child.attrib:
                continue
            if "ellipse" in style:
                continue
            if "rhombus" in style:
                continue
            if "shape" in style:
                continue
            if "fontStyle=4" in style or "<u>" in value:
                continue
            if "&quot;" in value or "^^" in value:
                continue
            concept = {}
            attribute_block = {}
            attribute_block["xml_object"] = child

            p1, p2, p3, p4 = get_corners_rect_child(child)

            # We need a second iteration because we need to know if there is a block
            # on top of the current block, that determines if we are dealing with a class or attributes
            for child2 in self.root:
                style2 = child2.attrib["style"] if "style" in child2.attrib else ""
                # Filter all the elements except attributes and classes
                if "text" in style2 or "edgeLabel" in style2:
                    continue
                if "edge" in child2.attrib:
                    continue
                if "ellipse" in style2:
                    continue
                if "rhombus" in style2:
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
                        attribute_value = attribute_value.split(">")[-1].strip()
                        attribute["prefix"] = attribute_value.split(":")[0].split(" ")[::-1][0]
                        attribute["uri"] = attribute_value.split(":")[1].split(" ")[0]
                        attribute["label"] = create_label(attribute["uri"], "property")

                        if len(attribute_value.split(":")) > 2:
                            final_datatype = attribute_value.split(":")[2].strip()
                            final_datatype = final_datatype[0].lower() + final_datatype[1:]
                            attribute["datatype"] = final_datatype
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
                        if len(attribute_value.split("..")) > 1:
                            min_card = attribute_value.split("..")[0][-1]
                            min_card = min_card.split(">")[-1]
                            attribute["min_cardinality"] = min_card.split("<")[0]
                        else:
                            attribute["min_cardinality"] = None

                        if attribute["min_cardinality"] == "0":
                            attribute["min_cardinality"] = None

                        if len(attribute_value.split("..")) > 1:
                            max_card = attribute_value.split("..")[1].split(")")[0]
                            max_card = max_card.split(">")[-1]
                            attribute["max_cardinality"] = max_card.split("<")[0]
                        else:
                            attribute["max_cardinality"] = None

                        if attribute["max_cardinality"] == "N":
                            attribute["max_cardinality"] = None

                        attributes.append(attribute)
                    attribute_block["attributes"] = attributes
                    attribute_block["concept_associated"] = child2.attrib["id"]
                    self.attribute_blocks[id] = attribute_block
                    attributes_found = True
                    break
            # If after a dense one to all evaluation the object selected cannot be associated
            # to any other object it means that it is a class
            if not attributes_found and value != "":
                value = value.split("</div>")
                value = [item for item in value if item != ""][0]
                value = value.split("<br>")
                value = [item for item in value if item != ""][0]
                concept["prefix"] = value.split(":")[0].strip()
                concept["uri"] = value.split(":")[-1].strip()
                concept["label"] = create_label(concept["uri"], "class")
                concept["xml_object"] = child
                self.concepts[id] = concept

        return self.concepts, self.attribute_blocks


    def find_elements(self):

        namespaces = self.find_namespaces()
        metadata = self.find_metadata()
        relations = self.find_relations()
        ellipses = self.find_ellipses()
        individuals = self.find_individuals()
        concepts, attribute_blocks = self.find_concepts_and_attributes()
        rhombuses = self.find_rhombuses()

        return concepts, attribute_blocks, relations, individuals, ellipses, metadata, namespaces, rhombuses
