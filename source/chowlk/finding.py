import re
import string
from source.chowlk.geometry import get_corners_rect_child
from source.chowlk.utils import clean_html_tags, clean_uri, create_label


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
        self.hexagons = {}
        self.anonimous_classes = {}
        self.errors = {
            "Concepts": [],
            "Arrows": [],
            "Ellipses": [],
            "Attributes": [],
            "Namespaces": [],
            "Metadata": [],
            "Rhombuses": [],
            "Hexagons": [],
            "Individual": [],
            "Cardinality-Restrictions": []
        }

    def find_relations(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = clean_html_tags(
                child.attrib["value"]) if "value" in child.attrib else None
            ellipse_connection_detected = False

            if "edge" not in child.attrib:
                continue

            relation = {}
            source = child.attrib["source"] if "source" in child.attrib else None
            target = child.attrib["target"] if "target" in child.attrib else None

            relation["source"] = source
            relation["target"] = target
            relation["xml_object"] = child

            source_xml_object = {}
            parent_xml_object = {}

            if value is None or len(value) == 0:
                # This bucle find the xml object of the source of the edge
                # and the xml object of the parent of the edge
                for child2 in self.root:
                    if source == child2.attrib["id"]:
                        source_xml_object = child2.attrib
                    elif id == child2.attrib["parent"]:
                        parent_xml_object = child2.attrib

                # Looking for ellipses
                if "style" in source_xml_object and ("ellipse" in source_xml_object["style"] or "hexagon" in source_xml_object["style"]) and parent_xml_object == {}:
                    # This edge is part of a unionOf / intersectionOf construct
                    # it is not useful beyond that construction
                    relation["type"] = "ellipse_connection"
                    self.relations[id] = relation
                    continue

                """for child2 in self.root:
                    style2 = child2.attrib["style"] if "style" in child2.attrib else ""
                    if source == child2.attrib["id"] and ("ellipse" in style2 or "hexagon" in style2):
                        # This edge is part of a unionOf / intersectionOf construct
                        # it is not useful beyond that construction
                        relation["type"] = "ellipse_connection"
                        ellipse_connection_detected = True
                        break
                if ellipse_connection_detected:
                    self.relations[id] = relation
                    continue"""

                # Sometimes edges have their value not embedded into the edge itself, at least not in the
                # "value" parameter of the object. We can track their associated value by looking for free text
                # and evaluating the "parent" parameter which will point to an edge.
                if "style" in parent_xml_object and ("text" in parent_xml_object["style"] or "edgeLabel" in parent_xml_object["style"]):
                    value = clean_html_tags(parent_xml_object["value"])

                """for child2 in self.root:
                    style2 = child2.attrib["style"] if "style" in child2.attrib else ""
                    if ("text" in style2 or "edgeLabel" in style2) and id == child2.attrib["parent"]:
                        value = clean_html_tags(child2.attrib["value"])
                        break"""

                if relation["source"] is None:
                    error = {
                        "message": "Domain side of the relation is not connected to any shape, please check this",
                        "shape_id": id,
                        "value": value
                    }
                    self.errors["Arrows"].append(error)

                if relation["target"] is None:
                    error = {
                        "message": "Range side of the relation is not connected to any shape, please check this",
                        "shape_id": id,
                        "value": value
                    }
                    self.errors["Arrows"].append(error)

                # If after the evaluation of free text we cannot find any related text to the edge
                # we can say for sure that it is a "subclass" or "type" relationship
                if value is None or len(value) == 0:
                    # Check for both sides of the edge, sometimes it can be tricky.
                    if "endArrow=block" in style or "startArrow=block" in style:
                        relation["type"] = "rdfs:subClassOf"
                    elif "endArrow=open" in style or "startArrow=open" in style:
                        relation["type"] = "rdf:type"
                    else:
                        error = {
                            "message": "Could not recognize type of arrow",
                            "shape_id": id,
                            "value": "No value"
                        }
                        self.errors["Arrows"].append(error)
                    self.relations[id] = relation
                    continue

            # Detection of special type of edges
            edge_types = ["rdfs:subClassOf", "rdf:type", "owl:equivalentClass", "owl:disjointWith", "owl:complementOf",
                          "rdfs:subPropertyOf", "owl:equivalentProperty", "owl:inverseOf", "rdfs:domain", "rdfs:range", "owl:sameAs", "owl:differentFrom"]

            edge_type_founded = False

            for edge_type in edge_types:
                if edge_type in value:
                    relation["type"] = edge_type
                    self.relations[id] = relation
                    edge_type_founded = True
                    break

            if edge_type_founded:
                continue

            # Domain Range evaluation
            if "dashed=1" in style:
                if "startArrow=oval" not in style or "startFill=0" in style:
                    relation["domain"] = False
                    relation["range"] = False
                elif "startFill=1" in style:
                    relation["domain"] = source
                    relation["range"] = False

            elif "dashed=1" not in style:
                if "startArrow=oval" not in style or "startFill=1" in style:
                    relation["domain"] = source
                    relation["range"] = target
                elif "startFill=0" in style:
                    relation["domain"] = False
                    relation["range"] = target

            # Existential Universal restriction evaluation
            if "allValuesFrom" in value or "(all)" in value or "∀" in value:
                relation["allValuesFrom"] = True
            else:
                relation["allValuesFrom"] = False

            if "someValuesFrom" in value or "(some)" in value or "∃" in value:
                relation["someValuesFrom"] = True
            else:
                relation["someValuesFrom"] = False

            # owl:hasValue
            if "hasValue" in value or "(value)" in value or "∋" in value:
                relation["hasValue"] = True
            else:
                relation["hasValue"] = False

            # class_description predicate restriction
            # A named class can be a subClass, an equivalentClass or disjointWith a class restriction
            # When the user wants to declare this relation, it is specified inside the "relation" in diagrams
            if "(sub)" in value:
                relation["predicate_restriction"] = "rdfs:subClassOf"
            elif "(eq)" in value:
                relation["predicate_restriction"] = "owl:equivalentClass"
            elif "(dis)" in value:
                relation["predicate_restriction"] = "owl:disjointWith"
            else:
                relation["predicate_restriction"] = "rdfs:subClassOf"

            # Property restriction evaluation
            relation["functional"] = True if "(F)" in value else False
            relation["inverse_functional"] = True if "(IF)" in value else False
            relation["transitive"] = True if "(T)" in value else False
            relation["symmetric"] = True if "(S)" in value else False

            # Prefix and uri
            try:

                uri = clean_uri(value)
                uri = uri.split("|")[-1].strip().split(">>")[-1].strip()

                # In order to implement @base directive
                # If uri contains ':' && uri does not start with ':' => normal prefix
                # If uri starts with ':' => empty prefix
                # If uri does not contain ':' => prefix is @base
                # If uri contains ':' && uri does not start with ':' => len(uri_split) > 1 and uri_split[0] != ""
                # If uri starts with ':' => len(uri_split) > 1 and uri_split[0] == ""
                # If uri does not contain ':' => len(uri_split) == 1
                uri_split = uri.split(":")
                if(len(uri_split) > 1):
                    # normal prefix || empty prefix (both are in namespace)
                    prefix = uri_split[0].strip()
                    if(prefix == ""):
                        prefix = "cambiar_a_prefijo_vacio"
                    uri = uri_split[-1].strip()
                else:
                    # prefix is @base
                    # store prefix with an auxiliar name in order
                    # write the relations with base directive in to write_object_properties
                    prefix = "<cambiar_a_base"
                    uri = uri_split[0].strip() + ">"

                """#Como estaba hecho antes
                print(uri)
                uri = uri.split("|")[-1].strip().split(">>")[-1].strip()
                print(uri)

                check = uri.split(":")[1] # Check if error in text

                prefix = uri.split(":")[0].strip()
                uri = uri.split(":")[-1].strip()

                check = prefix[0] # Check if error in text
                check = uri[0] # Check if error in text"""

                uri = re.sub(" ", "", uri)

                relation["prefix"] = prefix
                relation["uri"] = uri
                relation["label"] = create_label(relation["uri"], "property")
            except:
                error = {
                    "message": "Problems in the text of the arrow",
                    "shape_id": id,
                    "value": value
                }
                self.errors["Arrows"].append(error)
                continue

            # Cardinality restriction evaluation
            try:
                #max_min_card = re.findall("\(([0-9][^)]+)\)", value)
                max_min_card = re.findall("\((\S*[.][.]\S*)\)", value)
                max_min_card = max_min_card[-1] if len(
                    max_min_card) > 0 else None

                if max_min_card is None:
                    relation["min_cardinality"] = None
                    relation["max_cardinality"] = None
                else:
                    max_min_card = max_min_card.split("..")
                    relation["min_cardinality"] = max_min_card[0]
                    relation["max_cardinality"] = max_min_card[1]
            except:
                error = {
                    "message": "Problems in cardinality definition",
                    "shape_id": id,
                    "value": value
                }
                self.errors["Arrows"].append(error)
                continue

            # If min_cardinality == 0 this means it is not necessary to create
            # a min_cardinality restrictions
            if relation["min_cardinality"] == '0':
                relation["min_cardinality"] = None

            # If max_cardinality == N this means it is not necessary to create
            # a max_cardinality restrictions
            if relation["max_cardinality"] == 'N':
                relation["max_cardinality"] = None

            # Check if min_cardinality represents a non negative integer
            if relation["min_cardinality"] != None:
                try:
                    aux = float(relation["min_cardinality"])
                    if not aux.is_integer() or aux < 0:
                        message = ("min_cardinality is " + relation["min_cardinality"] +
                                   " which is not a non negative integer, in restriction " +
                                   relation["prefix"] + ":"
                                   + relation["uri"])
                        relation["min_cardinality"] = None
                        error = {
                            "message": message,
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Cardinality-Restrictions"].append(error)

                except:
                    print("\n relation")
                    print(relation)
                    print(value)
                    print(max_min_card)
                    message = ("min_cardinality is not a number, in relation "
                               + relation["prefix"] + ":"
                               + relation["uri"])
                    relation["min_cardinality"] = None
                    error = {
                        "message": message,
                        "shape_id": id,
                        "value": value
                    }
                    self.errors["Cardinality-Restrictions"].append(error)

            if relation["max_cardinality"] != None:
                # Check if max_cardinality represents a non negative integer
                try:
                    aux = float(relation["max_cardinality"])
                    if not aux.is_integer() or aux < 0:
                        message = ("max_cardinality is " + relation["max_cardinality"] +
                                   " which is not a non negative integer, in restriction " +
                                   relation["prefix"] + ":"
                                   + relation["uri"])
                        relation["max_cardinality"] = None
                        error = {
                            "message": message,
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Cardinality-Restrictions"].append(error)

                except:
                    message = ("max_cardinality is not a number, in restriction "
                               + relation["prefix"] + ":"
                               + relation["uri"])
                    relation["max_cardinality"] = None
                    error = {
                        "message": message,
                        "shape_id": id,
                        "value": value
                    }
                    self.errors["Cardinality-Restrictions"].append(error)

            if relation["min_cardinality"] == relation["max_cardinality"]:
                relation["cardinality"] = relation["min_cardinality"]
                relation["max_cardinality"] = None
                relation["min_cardinality"] = None
            else:
                relation["cardinality"] = None

            # max_cardinality must be greater than min_cardinality
            if(relation["max_cardinality"] != None and relation["min_cardinality"] != None
                    and float(relation["max_cardinality"]) < float(relation["min_cardinality"])):
                message = ("max_cardinality is lower than min_cardinality" +
                           " in restriction " + relation["prefix"] + ":"
                           + relation["uri"])
                relation["max_cardinality"] = None
                relation["min_cardinality"] = None
                error = {
                    "message": message,
                    "shape_id": id,
                    "value": value
                }
                self.errors["Cardinality-Restrictions"].append(error)

            relation["type"] = "owl:ObjectProperty"

            self.relations[id] = relation

        return self.relations

    def find_namespaces(self):

        for child in self.root:
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = child.attrib["value"] if "value" in child.attrib else ""
            # Dictionary of Namespaces
            if "shape=note" in style:
                text = clean_html_tags(value)
                namespaces = text.split("|")
                namespaces = [
                    item for item in namespaces if item.strip() != ""]
                for ns in namespaces:
                    try:
                        ns = ns.strip()
                        prefix = ns.split(":")[0].strip()
                        ontology_uri = ns.split("http")[-1].strip()
                        ontology_uri = "http" + ontology_uri
                        self.namespaces[prefix] = ontology_uri
                    except:
                        error = {
                            "message": "Problems in the text of the Namespace",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Namespaces"].append(error)
                        continue
        return self.namespaces

    def find_metadata(self):

        for child in self.root:

            style = child.attrib["style"] if "style" in child.attrib else ""
            value = child.attrib["value"] if "value" in child.attrib else ""
            # Dictionary of ontology level metadata
            if "shape=document" in style:
                text = clean_html_tags(value)
                annotations = text.split("|")
                for ann in annotations:
                    try:
                        ann_prefix = ann.split(":")[0].strip()
                        ann_type = ann.split(":")[1].strip()
                        if ann_type == "imports":
                            ann_value = ann.split(":")[2:]
                            ann_value = ":".join(ann_value).strip()
                        else:
                            ann_value = ann.split(":")[2].strip()
                        if ann_prefix + ":" + ann_type in self.ontology_metadata:
                            self.ontology_metadata[ann_prefix +
                                                   ":" + ann_type].append(ann_value)
                        else:
                            self.ontology_metadata[ann_prefix +
                                                   ":" + ann_type] = [ann_value]
                    except:
                        error = {
                            "message": "Problems in the text of the Metadata",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Metadata"].append(error)
                        continue

        return self.ontology_metadata

    def find_ellipses(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = child.attrib["value"] if "value" in child.attrib else None
            ellipse_corrupted = False
            try:
                if "ellipse" in style:
                    ellipse = {}
                    ellipse["xml_object"] = child
                    if "⨅" in value or "owl:intersectionOf" in value:
                        ellipse["type"] = "owl:intersectionOf"
                    elif "⨆" in value or "owl:unionOf" in value:
                        ellipse["type"] = "owl:unionOf"
                    elif "≡" in value:
                        ellipse["type"] = "owl:equivalentClass"
                    elif "⊥" in value:
                        ellipse["type"] = "owl:disjointWith"
                    elif "owl:oneOf" in value:
                        ellipse["type"] = "owl:oneOf"

                    # Find the associated concepts to this union / intersection restriction
                    ellipse["group"] = []

                    for relation_id, relation in self.relations.items():
                        if "type" not in relation:
                            continue

                        if relation["type"] == "ellipse_connection":
                            source_id = relation["source"]
                            if id == source_id:
                                target_id = relation["target"]
                                if target_id is None:
                                    ellipse_corrupted = True
                                    break
                                ellipse["group"].append(target_id)

                        # anonymousClass owl:complementOf anonymousClass
                        elif relation["type"] == "owl:complementOf":
                            source_id = relation["source"]
                            if id == source_id:
                                ellipse["group"].append(relation_id)

                        # anonymousClass objectProperty anonymousClass
                        elif relation["type"] == "owl:ObjectProperty":
                            source_id = relation["source"]
                            if id == source_id:
                                ellipse["group"].append(relation_id)

                    if len(ellipse["group"]) < 2:
                        ellipse_corrupted = True

                    if ellipse_corrupted:
                        continue

                    ellipse["xml_object"] = child
                    self.ellipses[id] = ellipse
            except:
                continue

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
                value = clean_html_tags(value)
                try:
                    # In order to implement @base directive
                    # If value contains ':' && value does not start with ':' => normal prefix
                    # If value starts with ':' => empty prefix (which is the same as @base)
                    # If value does not contain ':' => prefix is @base
                    # If value contains ':' && value does not start with ':' => len(value_split) > 1 and value_split[0] != ""
                    # If value starts with ':' => len(value_split) > 1 and value_split[0] == ""
                    # If value does not contain ':' => len(value_split) == 1

                    value_split = value.split(":")
                    if(len(value_split) > 1):
                        # normal prefix || empty prefix (both are in namespace)
                        individual["prefix"] = value_split[0].strip()
                        if(individual["prefix"] == ""):
                            individual["prefix"] = "cambiar_a_prefijo_vacio"
                        individual["uri"] = value_split[1].strip()
                    else:
                        # prefix is @base
                        # store concept["prefix"] with an auxiliar name in order
                        # write the concepts with base directive in to write_concepts
                        individual["prefix"] = "<cambiar_a_base"
                        individual["uri"] = value_split[0].strip() + ">"

                    """#Asi estaba hecho
                    individual["prefix"] = value.split(":")[0]
                    individual["uri"] = value.split(":")[1]
                    individual["prefix"][0] # Check if error
                    individual["uri"][1] # Check if error"""

                    individual["type"] = None

                    individual["uri"] = re.sub(" ", "", individual["uri"])

                except:
                    error = {
                        "message": "Problems in the text of the Individual",
                        "shape_id": id,
                        "value": value
                    }
                    self.errors["Individual"].append(error)
                    continue

                self.individuals[id] = individual

                continue

        return self.individuals

    def find_attribute_values(self):

        for child in self.root:

            id = child.attrib["id"]
            value = child.attrib["value"] if "value" in child.attrib else None

            if value is None:
                continue

            value = clean_html_tags(value)

            if "&quot;" in value or "\"" in value:
                attribute = {}
                attribute["xml_object"] = child
                attribute["type"] = None
                attribute["lang"] = None

                try:
                    # Finding the value
                    if "&quot;" in value:

                        attribute["value"] = value.split("&quot;")[1]
                    elif "\"" in value:
                        reg_exp = '"(.*?)"'
                        attribute["value"] = re.findall(reg_exp, value)[0]

                    # Finding the type
                    if "^^" in value:
                        attribute["type"] = value.split("^^")[-1]

                    elif "@" in value:
                        attribute["lang"] = value.split("@")[-1]

                except:
                    error = {
                        "message": "Problems in the text of the literal",
                        "shape_id": id,
                        "value": value
                    }
                    self.errors["Individual"].append(error)
                    continue

                self.attributes[id] = attribute

        return self.attributes

    def find_rhombuses(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value_html_clean = clean_html_tags(
                child.attrib["value"]) if "value" in child.attrib else None

            if "rhombus" in style:

                rhombus = {}
                rhombus["xml_object"] = child

                try:
                    type = value_html_clean.split(
                        ">>")[0].split("<<")[-1].strip()
                    rhombus["type"] = type

                    value = value_html_clean.split("|")[-1].strip()
                    value = value.split(">>")[-1].strip()

                    # In order to implement @base directive
                    # If uri contains ':' && uri does not start with ':' => normal prefix
                    # If uri starts with ':' => empty prefix
                    # If uri does not contain ':' => prefix is @base
                    # If uri contains ':' && uri does not start with ':' => len(value_split) > 1 and value_split[0] != ""
                    # If uri starts with ':' => len(value_split) > 1 and value_split[0] == ""
                    # If uri does not contain ':' => len(value_split) == 1
                    value_split = value.split(":")
                    if(len(value_split) > 1):
                        # normal prefix || empty prefix (both are in namespace)
                        prefix = value_split[0].strip()
                        if(prefix == ""):
                            prefix = "cambiar_a_prefijo_vacio"
                        uri = value_split[-1].strip()
                    else:
                        # prefix is @base
                        # store prefix with an auxiliar name in order
                        # write the relations with base directive in to write_object_properties
                        prefix = "<cambiar_a_base"
                        uri = value_split[0].strip() + ">"

                    """#Como estaba hecho antes
                    prefix = value.split(":")[0].strip()
                    uri = value.split(":")[1].strip()"""

                    uri = re.sub(" ", "", uri)

                    rhombus["prefix"] = prefix
                    rhombus["uri"] = uri

                    self.rhombuses[id] = rhombus

                except:
                    error = {
                        "shape_id": id,
                        "value": value_html_clean
                    }
                    self.errors["Rhombuses"].append(error)
                    continue

                if type == "owl:ObjectProperty":

                    relation_uris = []

                    for relation_id, relation in self.relations.items():
                        if "uri" in relation:
                            relation_uris.append(relation["uri"])

                    if uri not in relation_uris:

                        uri = re.sub(" ", "", uri)

                        relation = {}
                        relation["source"] = None
                        relation["target"] = None
                        relation["xml_object"] = child
                        relation["type"] = type
                        relation["prefix"] = prefix
                        relation["uri"] = uri
                        relation["label"] = create_label(uri, "property")
                        relation["domain"] = False
                        relation["range"] = False
                        relation["allValuesFrom"] = False
                        relation["someValuesFrom"] = False
                        relation["hasValue"] = False
                        relation["min_cardinality"] = False
                        relation["max_cardinality"] = False
                        relation["cardinality"] = False
                        relation["functional"] = False
                        relation["inverse_functional"] = False
                        relation["transitive"] = False
                        relation["symmetric"] = False

                    self.relations[id] = relation

                elif type == "owl:DatatypeProperty":

                    attribute_uris = []

                    for attribute_block_id, attribute_block in self.attribute_blocks.items():
                        attributes = attribute_block["attributes"]
                        for attribute in attributes:
                            attribute_uris.append(attribute["uri"])

                    if uri not in attribute_uris:
                        attribute = {}
                        attribute_block = {}
                        attribute_block["xml_object"] = child
                        attribute["prefix"] = prefix
                        attribute["uri"] = uri
                        attribute["label"] = create_label(uri, "property")
                        attribute["datatype"] = None
                        attribute["functional"] = False
                        attribute["domain"] = False
                        attribute["range"] = False
                        attribute["allValuesFrom"] = False
                        attribute["someValuesFrom"] = False
                        attribute["hasValue"] = False
                        attribute["min_cardinality"] = None
                        attribute["max_cardinality"] = None
                        attribute_block["attributes"] = [attribute]

                    self.attribute_blocks[id] = attribute_block

        return self.rhombuses, self.errors

    def find_hexagons(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = child.attrib["value"] if "value" in child.attrib else None
            ellipse_corrupted = False
            try:
                if "hexagon" in style:
                    hexagon = {}
                    hexagon["xml_object"] = child
                    if "owl:AllDifferent" in value:
                        hexagon["type"] = "owl:AllDifferent"
                    elif "owl:oneOf" in value:
                        hexagon["type"] = "owl:oneOf"

                    # Find the associated concepts to this union / intersection restriction
                    hexagon["group"] = []

                    for relation_id, relation in self.relations.items():

                        if "type" not in relation:
                            continue
                        if relation["type"] == "ellipse_connection":
                            # print("here")
                            source_id = relation["source"]
                            if id == source_id:
                                target_id = relation["target"]
                                if target_id is None:
                                    ellipse_corrupted = True
                                    break
                                hexagon["group"].append(target_id)

                    if len(hexagon["group"]) < 2:
                        ellipse_corrupted = True

                    if ellipse_corrupted:
                        continue

                    hexagon["xml_object"] = child
                    self.hexagons[id] = hexagon
            except:
                continue

        return self.hexagons

    def find_concepts_and_attributes(self):

        for child in self.root:

            id = child.attrib["id"]
            style = child.attrib["style"] if "style" in child.attrib else ""
            value = child.attrib["value"] if "value" in child.attrib else ""
            attributes_found = False

            try:
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
                """if "&quot;" in value or "^^" in value:
                    continue"""
                if "&quot;" in value:
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

                    p1_support, p2_support, p3_support, p4_support = get_corners_rect_child(
                        child2)
                    dx = abs(p1[0] - p2_support[0])
                    dy = abs(p1[1] - p2_support[1])

                    if dx < 5 and dy < 5:
                        attributes = []
                        value = clean_html_tags(value)
                        attribute_list = value.split("|")
                        domain = False if "dashed=1" in style else child2.attrib["id"]
                        for attribute_value in attribute_list:
                            attribute = {}
                            attribute_value_cleaned = clean_uri(
                                attribute_value)
                            try:

                                # get the prefix:uri
                                attribute_value_split = attribute_value_cleaned.split(" ")[
                                    0].strip()
                                # If the datatype has range => remove the last :
                                if(attribute_value_split[-1] == ":"):
                                    attribute_value_split = attribute_value_split[:-1]

                                # In order to implement @base directive
                                    # If value contains ':' && value does not start with ':' => normal prefix
                                    # If value starts with ':' => empty prefix (which is the same as @base)
                                    # If value does not contain ':' => prefix is @base
                                    # If value contains ':' && value does not start with ':' => len(value_split) > 1 and value_split[0] != ""
                                    # If value starts with ':' => len(value_split) > 1 and value_split[0] == ""
                                    # If value does not contain ':' => len(value_split) == 1

                                attribute_value_split = attribute_value_split.split(
                                    ":")
                                if(len(attribute_value_split) > 1):
                                    # normal prefix || empty prefix (both are in namespace)
                                    attribute["prefix"] = attribute_value_split[0].strip(
                                    )
                                    if(attribute["prefix"] == ""):
                                        attribute["prefix"] = "cambiar_a_prefijo_vacio"
                                    attribute["uri"] = attribute_value_split[1].strip(
                                    )
                                else:
                                    # prefix is @base
                                    # store concept["prefix"] with an auxiliar name in order
                                    # write the concepts with base directive in to write_concepts
                                    attribute["prefix"] = "<cambiar_a_base"
                                    attribute["uri"] = attribute_value_split[0].strip(
                                    ) + ">"

                                """print(attribute_value_cleaned.split(":"))
                                attribute["prefix"] = attribute_value_cleaned.split(":")[0].strip()
                                attribute["prefix"][0] # Check if error in text
                                attribute["uri"] = attribute_value_cleaned.split(":")[1].strip()
                                
                                # Taking into account possible spaces in the uri of the concept
                                attribute["uri"] = re.sub(" ", "", attribute["uri"])

                                attribute["prefix"][1] # Check if error in text
                                attribute["label"] = create_label(attribute["uri"], "property")"""

                                attribute["uri"] = re.sub(
                                    " ", "", attribute["uri"])
                                attribute["label"] = create_label(
                                    attribute["uri"], "property")

                            except:
                                error = {
                                    "message": "Problems in the text of the attribute",
                                    "shape_id": id,
                                    "value": attribute_value_cleaned
                                }
                                self.errors["Attributes"].append(error)
                                continue

                            try:
                                if(attribute["prefix"] != "<cambiar_a_base"):
                                    if len(attribute_value.split(":")) > 2:
                                        final_datatype = attribute_value.split(
                                            ":")[-1].strip()
                                        final_datatype = final_datatype[0].lower(
                                        ) + final_datatype[1:]
                                        attribute["datatype"] = final_datatype
                                        if len(attribute_value.split(":")) > 3:
                                            attribute["prefix_datatype"] = attribute_value.split(":")[
                                                2].strip()
                                            if (attribute["prefix_datatype"] == ""):
                                                attribute["prefix_datatype"] = "cambiar_a_prefijo_vacio"
                                        else:
                                            attribute["prefix_datatype"] = "xsd"
                                    else:
                                        attribute["datatype"] = None

                                else:
                                    if len(attribute_value.split(":")) > 1:
                                        final_datatype = attribute_value.split(
                                            ":")[-1].strip()
                                        final_datatype = final_datatype[0].lower(
                                        ) + final_datatype[1:]
                                        attribute["datatype"] = final_datatype
                                        if len(attribute_value.split(":")) > 2:
                                            attribute["prefix_datatype"] = attribute_value.split(":")[
                                                1].strip()
                                        else:
                                            attribute["prefix_datatype"] = "xsd"
                                    else:
                                        attribute["datatype"] = None
                            except:
                                error = {
                                    "message": "Problems in the datatype of the attribute",
                                    "shape_id": id,
                                    "value": attribute_value_cleaned
                                }
                                self.errors["Attributes"].append(error)
                                continue

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

                            # owl:hasValue
                            if "(value)" in attribute_value or "∋" in attribute_value:
                                # In these cases the object is a data value of the form
                                # "data_value"^^prefix_datatype:datatype
                                attribute["hasValue"] = True

                            else:
                                attribute["hasValue"] = False

                            # class_description predicate restriction
                            # A named class can be a subClass, an equivalentClass or disjointWith a class restriction
                            # When the user wants to declare this relation, it is specified inside the "relation" in diagrams
                            if "(sub)" in attribute_value:
                                attribute["predicate_restriction"] = "rdfs:subClassOf"
                            elif "(eq)" in attribute_value:
                                attribute["predicate_restriction"] = "owl:equivalentClass"
                            elif "(dis)" in attribute_value:
                                attribute["predicate_restriction"] = "owl:disjointWith"
                            else:
                                attribute["predicate_restriction"] = "rdfs:subClassOf"

                            attribute["functional"] = True if "(F)" in attribute_value else False

                            # Cardinality restriction evaluation
                            try:
                                #max_min_card = re.findall("\(([0-9][^)]+)\)", attribute_value)
                                max_min_card = re.findall(
                                    "\((\S*[.][.]\S*)\)", attribute_value)
                                max_min_card = max_min_card[-1] if len(
                                    max_min_card) > 0 else None
                                if max_min_card is None:
                                    attribute["min_cardinality"] = None
                                    attribute["max_cardinality"] = None
                                else:
                                    max_min_card = max_min_card.split("..")
                                    attribute["min_cardinality"] = max_min_card[0]
                                    attribute["max_cardinality"] = max_min_card[1]
                            except:
                                error = {
                                    "message": "Problems in cardinality definition",
                                    "shape_id": id,
                                    "value": attribute_value_cleaned
                                }
                                self.errors["Attributes"].append(error)
                                continue

                            # If min_cardinality == 0 this means it is not necessary to create
                            # a min_cardinality restrictions
                            if attribute["min_cardinality"] == '0':
                                attribute["min_cardinality"] = None

                            # If max_cardinality == N this means it is not necessary to create
                            # a max_cardinality restrictions
                            if attribute["max_cardinality"] == 'N':
                                attribute["max_cardinality"] = None

                            # Check if min_cardinality represents a non negative integer
                            if attribute["min_cardinality"] != None:
                                try:
                                    aux = float(attribute["min_cardinality"])
                                    if not aux.is_integer() or aux < 0:
                                        message = ("min_cardinality is " + attribute["min_cardinality"] +
                                                   " which is not a non negative integer, in restriction " +
                                                   attribute["prefix"] + ":"
                                                   + attribute["uri"])
                                        attribute["min_cardinality"] = None
                                        error = {
                                            "message": message,
                                            "shape_id": id,
                                            "value": attribute_value_cleaned
                                        }
                                        self.errors["Cardinality-Restrictions"].append(
                                            error)

                                except:
                                    message = ("min_cardinality is not a number, in attribute "
                                               + attribute["prefix"] + ":"
                                               + attribute["uri"])
                                    attribute["min_cardinality"] = None
                                    error = {
                                        "message": message,
                                        "shape_id": id,
                                        "value": attribute_value_cleaned
                                    }
                                    self.errors["Cardinality-Restrictions"].append(
                                        error)

                            if attribute["max_cardinality"] != None:
                                # Check if max_cardinality represents a non negative integer
                                try:
                                    aux = float(attribute["max_cardinality"])
                                    if not aux.is_integer() or aux < 0:
                                        message = ("max_cardinality is " + attribute["max_cardinality"] +
                                                   " which is not a non negative integer, in restriction " +
                                                   attribute["prefix"] + ":"
                                                   + attribute["uri"])
                                        attribute["max_cardinality"] = None
                                        error = {
                                            "message": message,
                                            "shape_id": id,
                                            "value": attribute_value_cleaned
                                        }
                                        self.errors["Cardinality-Restrictions"].append(
                                            error)

                                except:
                                    message = ("max_cardinality is not a number, in restriction "
                                               + attribute["prefix"] + ":"
                                               + attribute["uri"])
                                    attribute["max_cardinality"] = None
                                    error = {
                                        "message": message,
                                        "shape_id": id,
                                        "value": attribute_value_cleaned
                                    }
                                    self.errors["Cardinality-Restrictions"].append(
                                        error)

                            if attribute["min_cardinality"] == attribute["max_cardinality"]:
                                attribute["cardinality"] = attribute["min_cardinality"]
                                attribute["min_cardinality"] = None
                                attribute["max_cardinality"] = None
                            else:
                                attribute["cardinality"] = None

                            # max_cardinality must be greater than min_cardinality
                            if(attribute["max_cardinality"] != None and attribute["min_cardinality"] != None
                                    and float(attribute["max_cardinality"]) < float(attribute["min_cardinality"])):
                                message = ("max_cardinality is lower than min_cardinality" +
                                           " in restriction " +
                                           attribute["prefix"] + ":"
                                           + attribute["uri"])
                                attribute["max_cardinality"] = None
                                attribute["min_cardinality"] = None
                                error = {
                                    "message": message,
                                    "shape_id": id,
                                    "value": attribute_value_cleaned
                                }
                                self.errors["Cardinality-Restrictions"].append(
                                    error)

                            attributes.append(attribute)

                        attribute_block["attributes"] = attributes
                        attribute_block["concept_associated"] = child2.attrib["id"]
                        self.attribute_blocks[id] = attribute_block
                        attributes_found = True
                        break
                # If after a dense one to all evaluation the object selected cannot be associated
                # to any other object it means that it is a class
                #value = clean_html_tags(value).strip()
                if not attributes_found and value != "":

                    # First we have to verify they are actually concepts

                    # One way is to verify breaks in the text
                    value = clean_html_tags(value).strip()
                    if "|" in value:
                        error = {
                            "message": "Problems in text of the Concept",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Concepts"].append(error)

                        continue

                    # Other option is to verify things like functionality, some, all, etc.
                    if "(F)" in value or "(some)" in value or "(all)" in value or "∀" in value or "∃" in value:
                        error = {
                            "message": "Attributes not attached to any concept",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Attributes"].append(error)
                        continue

                    # If datatype is mentioned
                    if len(value.split(":")) > 2:
                        error = {
                            "message": "Attributes not attached to any concept",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Attributes"].append(error)
                        continue

                    # If cardinality is indicated
                    if len(value.split("..")) > 1:
                        error = {
                            "message": "Attributes not attached to any concept",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Attributes"].append(error)
                        continue

                    if "\"" in value:
                        continue

                    value = clean_html_tags(value)
                    try:

                        # In order to implement @base directive
                        # If value contains ':' && value does not start with ':' => normal prefix
                        # If value starts with ':' => empty prefix (which is the same as @base)
                        # If value does not contain ':' => prefix is @base
                        # If value contains ':' && value does not start with ':' => len(value_split) > 1 and value_split[0] != ""
                        # If value starts with ':' => len(value_split) > 1 and value_split[0] == ""
                        # If value does not contain ':' => len(value_split) == 1

                        value_split = value.split(":")
                        if(len(value_split) > 1):
                            # normal prefix || empty prefix (both are in namespace)
                            concept["prefix"] = value_split[0].strip()
                            if(concept["prefix"] == ""):
                                concept["prefix"] = "cambiar_a_prefijo_vacio"
                            concept["uri"] = value_split[1].strip()
                        else:
                            # prefix is @base
                            # store concept["prefix"] with an auxiliar name in order
                            # write the concepts with base directive in to write_concepts
                            concept["prefix"] = "<cambiar_a_base"
                            concept["uri"] = value_split[0].strip() + ">"

                        """#Como estaba hecho antes
                        concept["prefix"] = value.split(":")[0].strip()
                        concept["uri"] = value.split(":")[1].strip()

                        concept["prefix"][0] # Check if error
                        concept["uri"][1] # Check if error"""

                        # Taking into account possible spaces in the uri of the concept
                        concept["uri"] = re.sub(" ", "", concept["uri"])

                        concept["label"] = create_label(
                            concept["uri"], "class")
                        concept["xml_object"] = child
                    except:
                        error = {
                            "message": "Problems in text of the concept",
                            "shape_id": id,
                            "value": value
                        }
                        self.errors["Concepts"].append(error)
                        continue

                    self.concepts[id] = concept

                elif not attributes_found and value == "":
                    anonymousClass = {}
                    anonymousClass["xml_object"] = child
                    anonymousClass["relations"] = []
                    self.anonimous_classes[id] = anonymousClass

            except:
                # print("here")
                continue

        return self.concepts, self.attribute_blocks, self.anonimous_classes

    def find_elements(self):

        namespaces = self.find_namespaces()
        metadata = self.find_metadata()
        relations = self.find_relations()
        ellipses = self.find_ellipses()
        hexagons = self.find_hexagons()
        individuals = self.find_individuals()
        concepts, attribute_blocks, anonimous_classes = self.find_concepts_and_attributes()
        rhombuses, errors = self.find_rhombuses()

        return concepts, attribute_blocks, relations, individuals, ellipses, hexagons, metadata, namespaces, rhombuses, errors, anonimous_classes
