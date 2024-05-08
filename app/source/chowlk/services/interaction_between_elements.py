import re
from app.source.chowlk.resources.utils import create_label, clean_html_tags
from app.source.chowlk.resources.utils import base_directive_prefix
from app.source.chowlk.services.individual_associations import datatype_relation_association
from app.source.chowlk.services.class_associations import resolve_concept_reference

# This class store the functions which add more information to the classified elements which are identified in the
# diagram_model trough the interaction between other xml elements.
# (e.g. if the source of an arrow is an ellipse it is neccsary to store that information in the ellipse)
def interaction_between_elements(diagram_model):
    add_value_to_empty_arrows(diagram_model)
    classify_boxes_into_classes_and_datatype_properties(diagram_model)
    resolve_concept_reference(diagram_model)
    datatype_relation_association(diagram_model)
    check_default_annotations(diagram_model)
    add_relations_to_hexagons_and_ellipses(diagram_model)
    check_ellipses_relations(diagram_model)
    check_hexagons_relations(diagram_model)
    rhombus_relations(diagram_model)
    find_annotations_properties(diagram_model)

# This function classify each of the boxes into a concept or an attribute.
# An attribute is always underneath another box.
# A concept can not be underneath another box.
def classify_boxes_into_classes_and_datatype_properties(diagram_model):
    # Get the attributes of the diagram model
    boxes = diagram_model.get_boxes()
    individuals = diagram_model.get_individuals()
    arrows = diagram_model.get_arrows()

    # For each box (box_1) check if there is another box (box_2) above it
    # (i.e. upper left corner of box_1 matches with the bottom left corner of box_2).
    for box_id_1, box_1 in boxes.items():
        value = box_1['value']

        # It is neccesary just to find one box above in order to be classiy as an attribute
        attributes_found = False

        for box_id_2, box_2 in boxes.items():

            # Are they the same element?
            if box_id_1 == box_id_2:
                continue
            
            # Get upper left corner
            p1 = box_1['p1']
            # Get bottom left corner
            p2_support = box_2['p2']
            # Calculate the distance between two points
            dx = abs(p1[0] - p2_support[0])
            dy = abs(p1[1] - p2_support[1])

            # Are the dots close enough?
            if dx < 5 and dy < 5:
                # box_1 is an attribute (is below another box)
                diagram_model.add_datatype_property(box_1['child'], value, box_id_1, box_1['style'], box_2['child'])
                # It is not neccesary to continue the searching
                attributes_found = True
                break
        
        # If after a dense one to all evaluation the object selected cannot be associated
        # to any other object it means that it is a class (named or unnamed)
        if not attributes_found:
            # Is it a named class?
            if value != '':
                diagram_model.add_class(value, box_id_1, box_1['child'])
            
            else:
                # In this case the box can be an anonymous class or an anonymous individual
                # The box represents an anonymous individual if there is an arrow whose target is this box,
                # whose source is a named individual and the arrow is representing an object property

                # Variable to check if an arrow that satisfied the conditions has been found
                anonymous_class = True

                # Iterate all the arrows
                for arrow_id, arrow in arrows.items():

                    # Is the target of the arrow this blank box?
                    if 'target' in arrow and arrow['target'] == box_id_1:

                        # Has been the arrow been identified as an object property?
                        if 'type' in arrow and arrow['type'] == 'owl:ObjectProperty':

                            # Is the source of the arrow a named individual?
                            if 'source' in arrow and arrow['source'] in individuals:
                                diagram_model.add_anonymous_individual(box_1['child'], box_id_1)
                                anonymous_class = False
                                break
                
                if anonymous_class:
                    # It is an unnamed class
                    diagram_model.add_anonymous_class(box_1['child'], box_id_1)

# This functionc check if the nameless arrow have an associated xml element containing its name or
# if they are special arrows (i.e. type, subclassOf or ellipse connections).
# An ellipse connection is a nameless arrow whose source is an ellipse. These kind of arrow look the same
# as the rdf:type arrows.
def add_value_to_empty_arrows(diagram_model):
    # Get the attributes of the diagram model
    arrows_without_value = diagram_model.get_arrows_without_value()
    arrows_parent = diagram_model.get_arrows_parent()
    ellipses = diagram_model.get_ellipses()
    hexagons = diagram_model.get_hexagons()
    arrows = diagram_model.get_arrows()

    for arrow_id, arrow in arrows_without_value.items():
        source = arrow["source"]
        style = arrow.pop("style")
        value = None

        # Is there an xml element associated to the arrow?
        if arrow_id in arrows_parent:
            value = arrows_parent[arrow_id]

        # Does the xml element associated to the arrow have a name?
        if value is None or len(value) == 0:

            # Has the arrow a source element from which it departs?
            if arrow["source"] is None:
                diagram_model.generate_error("The origin of a nameless arrow is not connected to any shape, please check this.", arrow_id, None, "Arrows")

            # Has the arrow a target element on which it ends?
            if arrow["target"] is None:
                diagram_model.generate_error("The end of of a nameless arrow is not connected to any shape, please check this.", arrow_id, None, "Arrows")

            # Is the source of the arrow an ellipse?
            if source in ellipses or source in hexagons:
                # This edge is part of a unionOf / intersectionOf / oneOf / owl:AllDifferent construct it is not useful beyond that construction
                arrow["type"] = "ellipse_connection"

            # If after the evaluation of free text we cannot find any related text to the edge
            # we can say for sure that it is a "subclass" or "type" relationship
            # Check for both sides of the edge, sometimes it can be tricky.
            elif "endArrow=block" in style or "startArrow=block" in style:
                arrow["type"] = "rdfs:subClassOf"
            elif "endArrow=open" in style or "startArrow=open" in style:
                arrow["type"] = "rdf:type"
            else:
                diagram_model.generate_error("Could not recognize type of arrow", arrow_id, None, "Arrows")
                continue
                
            arrows[arrow_id] = arrow

        else:
            diagram_model.add_value_to_arrow(arrow, value, style, arrow_id)

# This function check if the uri references of a default annotation property 
# has been wrongly classified as a class.
def check_default_annotations(diagram_model):
    classes = diagram_model.get_classes()
    arrows = diagram_model.get_arrows()
    uri_references = diagram_model.get_uri_references()

    for arrow_id, arrow in arrows.items():
        arrow_type = arrow['type'] if 'type' in arrow else ''

        # Is the arrow a default annotation property?
        if arrow_type == 'owl:AnnotationProperty':
            target_id = arrow['target'] if 'target' in arrow else ''
            # Has been the target of an annotation property identified as a concept?
            if target_id in classes:
                concept = classes[target_id]
                # It is an uri reference if it does not have a prefix defined and its suffix is between <>
                if concept['prefix'] == '':
                    suffix = concept['uri']
                    if suffix[0] == '<' and suffix[-1] == '>':
                        # It is an URI reference
                        uri_references[target_id] = suffix
                        # The URI reference has been classified wrongly as a concept
                        del classes[target_id]

# This function checks whether the arrow whose origin is an ellipse is valid 
# (if the notation allows such arrows to come from an ellipse).
# For example, the source of an rdfs:subClassOf arrow can not be an ellipse.
# If the type of the arrow is valid, store the arrow identifier in the source ellipse
# in order to make easier the generation of the corresponding triple in the "writer module".
def add_relation_to_ellipse(diagram_model, arrow, ellipse, source_id, arrow_id):
        
    # Does the arrow have a valid type?
    if arrow["type"] == "ellipse_connection":
        # Get the target of the arrow
        target_id = arrow["target"]

        # Is the end of the arrow not connected to an element?
        if target_id is None:
            # Generate an error
            ellipse_type = ellipse["type"]

            if ellipse_type == 'owl:unionOf' or ellipse_type == 'owl:intersectionOf' or ellipse_type == 'owl:equivalentClass':
                # There is a specific category for these kinds of ellipses
                ellipse_type = ellipse_type[4:]

            else:
                # General categories for ellipses
                ellipse_type = "Ellipses" 

            diagram_model.generate_error("An arrow of an " + ellipse["type"] +" is not connected to any shape, please check this", source_id, None, ellipse_type)
        
        else:
            # Store the identifier of the element connected to the ellipse
            ellipse["group"].append(target_id)

    # Does the arrow represent an owl:complementOf?
    elif arrow["type"] == "owl:complementOf":
        # The element connected to the ellipse represents an anonymous class
        ellipse["group"].append(arrow_id)

    # Does the arrow represent a restriction?
    elif arrow["type"] == "owl:ObjectProperty":
        # The element connected to the ellipse represents an anonymous class
        ellipse["group"].append(arrow_id)

    else:
        diagram_model.generate_error("The source of a" + arrow['type'] + " arrow is an ellipse. This kind of arrows can not comes from an ellipse, please check this", arrow_id, None, "Arrows")


# Function to check if an ellipse has the minimum of neccesary arrows
# An ellipse has to be connected to a minimum of two elements
def check_ellipses_relations(diagram_model):
    # Get the attributes of the diagram model
    ellipses = diagram_model.get_ellipses()
    # Array for storing the identifiers of the elements that do not fulfil the conditions
    borrar = []

    # Iterate all the ellipses
    for ellipse_id, ellipse in ellipses.items():

        # Is the ellipse connected to at least two elements?
        if len(ellipse["group"]) < 2:
            ellipse_type = ellipse["type"]

            # Is there a specific error category?
            if ellipse_type == 'owl:unionOf' or ellipse_type == 'owl:intersectionOf' or ellipse_type == 'owl:equivalentClass':
                ellipse_type = ellipse_type[4:]

            else:
                # Default ellipse category
                ellipse_type = 'Ellipses'

            diagram_model.generate_error("An " + ellipse["type"] + " is connected to less than two shapes. An " + ellipse["type"] + " needs at least two class axioms", ellipse_id, None, ellipse_type)
            borrar.append(ellipse_id)
            
    # Remove the elements which do not fulfil the conditions
    for ellipse_id in borrar:
        del ellipses[ellipse_id]

# This function finds the arrows whose source is an hexagon or an ellipse.
def add_relations_to_hexagons_and_ellipses(diagram_model):
    # Get the attributes of the diagram model
    arrows = diagram_model.get_arrows()
    ellipses = diagram_model.get_ellipses()
    hexagons = diagram_model.get_hexagons()

    # Iterate all the arrows
    for arrow_id, arrow in arrows.items():

        # Does the arrow have an error?
        if "type" not in arrow:
            continue

        source_id = arrow["source"]

        # Is the source of the arrow an ellipse?
        if source_id in ellipses:
            add_relation_to_ellipse(diagram_model, arrow, ellipses[source_id], source_id, arrow_id)
        
        # Is the source of the arrow an hexagon?
        elif source_id in hexagons:
            add_relation_to_hexagon(diagram_model, arrow, hexagons[source_id], source_id)

# This function checks whether the arrow whose origin is an hexagon is valid 
# (if the notation allows such arrows to come from an ellipse).
# For example, the source of an rdfs:subClassOf arrow can not be an hexagon.
# If the type of the arrow is valid, store the arrow identifier in the source hexagon
# in order to make easier the generation of the corresponding triple in the "writer module".
def add_relation_to_hexagon(diagram_model, arrow, hexagon, source_id):

    # Does the arrow have a valid type?
    if arrow["type"] == "ellipse_connection":
        # Get the target of the arrow
        target_id = arrow["target"]

        # Is the end of the arrow not connected to an element?
        if target_id is None:
            # Generate an error
            type = hexagon["type"]

            if type == 'owl:oneOf':
                # There is a specific category for owl:oneOf hexagons
                type = type[4:]

            else:
                # General categories for hexagons
                type = "Hexagons" 

            diagram_model.generate_error("An arrow of an " + hexagon["type"] +" is not connected to any shape, please check this", source_id, None, type)
        
        else:
            # Store the identifier of the element connected to the hexagon
            hexagon["group"].append(target_id)

# This function check if the hexagons are connected to a minimum of elements.
# An owl:AllDifferent hexagon has to be connected to at least three elements.
# An owl:oneOf hexagon has to be connected to at least one element.
def check_hexagons_relations(diagram_model):
    # Get the attributes of the diagram model
    hexagons = diagram_model.get_hexagons()
    # Array for storing the identifiers of the elements that do not fulfil the conditions
    borrar = []

    # Iterate all the hexagons
    for hexagon_id, hexagon in hexagons.items():

        # Does the hexagon represents an owl:AllDifferent hexagon which is connected to less than two elements?
        if hexagon["type"] == "owl:AllDifferent" and len(hexagon["group"]) < 2:
            diagram_model.generate_error("An owl:AllDifferent hexagon is connected to less than two elements. An owl:AllDifferent needs at least two individuals", hexagon_id, None, "Hexagons")
            borrar.append(hexagon_id)

        # Does the hexagon represents an owl:oneOf hexagon which is connected to less than one elements?
        elif hexagon["type"] == "owl:oneOf" and len(hexagon["group"]) < 1:
            diagram_model.generate_error("An owl:oneOf is connected to less than one shape. A owl:oneOf needs at least one individual", hexagon_id, None, "oneOf")
            borrar.append(hexagon_id)
    
    # Remove the elements which do not fulfil the conditions
    for hexagon_id in borrar:
        del hexagons[hexagon_id]

# Function to create an arrow or an attribute dictionary for each property (annotation, object or datatyoe)
# defined in a rhombus. It is neccesary to store the information in the arrows or attributes dictionary
# because these dictionary are going to be iterate in the write_model to declarate each property.
def rhombus_relations(diagram_model):
    # Get the attributes of the diagram model
    arrows = diagram_model.get_arrows()
    datatype_properties = diagram_model.get_datatype_properties()
    rhombuses = diagram_model.get_rhombuses()

    # Iterate all the rhombus
    for rhombus_id, rhombus in rhombuses.items():

        # Has the user defined an object property?
        if "owl:ObjectProperty" in rhombus['type']:
            # There is an object property defined in a rhombus which has not been defined in an arrow.
            # It is neccesary to add that object property to the arrows dictionary.
            arrows[rhombus_id] = create_object_property_from_rhombus(rhombus)

        # Has the user defined a datatype property?
        elif "owl:DatatypeProperty" in rhombus['type']:  
            # There is a datatype property defined in a rhombus which has not been defined in an attribute.
            # It is neccesary to add that datatype property to the attributes dictionary.
            datatype_properties[rhombus_id] = create_datatype_property_from_rhombus(rhombus)

        # Has the user defined an annotation property?
        elif "owl:AnnotationProperty" in rhombus['type']:
            # There is an annotation property defined in a rhombus which has not been defined in an arrow.
            # It is neccesary to add that annotation property to the arrows dictionary.
            arrows[rhombus_id] = create_annotation_property_from_rhombus(rhombus)
        
        # Has the user defined a functional property?
        elif 'owl:FunctionalProperty' in rhombus['type']:
            #In this case it is not clear if the user means to create an object property or a datatype property.
            # In this case just a property which is functional is created.
            arrows[rhombus_id] = create_functional_property_from_rhombus(rhombus)
        
        # else:
            # This case does not exist because chowlk creates the rhombus dictionary and all cases are covered above.

# Function to create an object property from a rhombus
def create_object_property_from_rhombus(rhombus):
    uri = re.sub(" ", "", rhombus['uri'])
    types = rhombus['additional_types'] if 'additional_types' in rhombus else ''
    # Create a new arrow dictionary
    arrow = {}
    arrow["source"] = None
    arrow["target"] = None
    arrow["xml_object"] = rhombus['xml_object']
    arrow["type"] = "owl:ObjectProperty"
    arrow["prefix"] = rhombus['prefix']
    arrow["uri"] = uri
    arrow["label"] = create_label(rhombus['prefix'], uri, "property")
    arrow["domain"] = False
    arrow["range"] = False
    arrow["allValuesFrom"] = False
    arrow["someValuesFrom"] = False
    arrow["hasValue"] = False
    arrow["min_cardinality"] = False
    arrow["max_cardinality"] = False
    arrow["cardinality"] = False
    arrow["functional"] = True if "owl:FunctionalProperty" in types else False
    arrow["inverse_functional"] = True if "owl:InverseFunctionalProperty" in types else False
    arrow["transitive"] = True if "owl:TransitiveProperty" in types else False
    arrow["symmetric"] = True if "owl:SymmetricProperty" in types else False
    arrow['deprecated'] = rhombus['deprecated']
    arrow["reflexive"] = True if "owl:ReflexiveProperty" in types else False
    arrow["asymmetric"] = True if "owl:AsymmetricProperty" in types else False
    arrow["irreflexive"] = True if "owl:IrreflexiveProperty" in types else False
    
    return arrow

# Function to create a datatype property from a rhombus
def create_datatype_property_from_rhombus(rhombus):
    types = rhombus['additional_types']
    # Create a new dictionary
    attribute = {}
    attribute_block = {}
    attribute_block["xml_object"] = rhombus['xml_object']
    attribute["prefix"] = rhombus['prefix']
    attribute["uri"] = rhombus['uri']
    attribute["label"] = create_label(rhombus['prefix'], rhombus['uri'], "property")
    attribute["datatype"] = None
    attribute["functional"] = True if "owl:FunctionalProperty" in types else False
    attribute["domain"] = False
    attribute["range"] = False
    attribute["allValuesFrom"] = False
    attribute["someValuesFrom"] = False
    attribute["hasValue"] = False
    attribute["min_cardinality"] = None
    attribute["max_cardinality"] = None
    attribute['deprecated'] = rhombus['deprecated']
    attribute_block["attributes"] = [attribute]
    
    return attribute_block

# Function to create an annotation property from a rhombus
def create_annotation_property_from_rhombus(rhombus):
    uri = re.sub(" ", "", rhombus['uri'])
    # Create a new dictionary
    arrow = {}
    arrow["source"] = None
    arrow["target"] = None
    arrow["xml_object"] = rhombus['xml_object']
    arrow["type"] = "owl:AnnotationProperty"
    arrow["prefix"] = rhombus['prefix']
    arrow["uri"] = uri
    arrow["label"] = create_label(rhombus['prefix'], uri, "property")
    arrow["domain"] = False
    arrow["range"] = False
    arrow["allValuesFrom"] = False
    arrow["someValuesFrom"] = False
    arrow["hasValue"] = False
    arrow["min_cardinality"] = False
    arrow["max_cardinality"] = False
    arrow["cardinality"] = False
    arrow["functional"] = False
    arrow["inverse_functional"] = False
    arrow["transitive"] = False
    arrow["symmetric"] = False
    arrow["reflexive"] = False
    arrow["asymmetric"] = False
    arrow["irreflexive"] = False
    
    return arrow

# Function to create a functional property from a rhombus
def create_functional_property_from_rhombus(rhombus):
    types = rhombus['additional_types']
    # Create a new dictionary
    arrow = {}
    arrow["source"] = None
    arrow["target"] = None
    arrow["xml_object"] = rhombus["xml_object"]
    arrow["type"] = "owl:FunctionalProperty"
    arrow["prefix"] = rhombus["prefix"]
    arrow["uri"] = rhombus["uri"]
    arrow["label"] = create_label(rhombus["prefix"], rhombus["uri"], "property")
    arrow["domain"] = False
    arrow["range"] = False
    arrow["allValuesFrom"] = False
    arrow["someValuesFrom"] = False
    arrow["hasValue"] = False
    arrow["min_cardinality"] = False
    arrow["max_cardinality"] = False
    arrow["cardinality"] = False
    arrow["functional"] = True
    arrow["inverse_functional"] = True if "owl:InverseFunctionalProperty" in types else False
    arrow["transitive"] = True if "owl:TransitiveProperty" in types else False
    arrow["symmetric"] = True if "owl:SymmetricProperty" in types else False
    arrow['deprecated'] = rhombus['deprecated']
    arrow["reflexive"] = True if "owl:ReflexiveProperty" in types else False
    arrow["asymmetric"] = True if "owl:AsymmetricProperty" in types else False
    arrow["irreflexive"] = True if "owl:IrreflexiveProperty" in types else False

    return arrow

# Function that identifies which relations are annotation properties.
# This relations are missclassified as object properties, but they have been
# defined as an annotation property through a rhombus.
# Moreover, for this relations its check if the target of the relation is an URI reference
def find_annotations_properties(diagram_model):

    # Get the attributes of the diagram model
    rhombuses = diagram_model.get_rhombuses()
    arrows = diagram_model.get_arrows()
    arrows_name = diagram_model.get_arrows_name()
    classes = diagram_model.get_classes()
    uri_references = diagram_model.get_uri_references()

    # For each rhombus whose type is "owl:AnnotationProperty" check if there is an arrow with the same name.
    # Iterate all the rhombuses
    for rhombus_id, rhombus in rhombuses.items():

        # Is the rhombus an annotation property?
        if rhombus['type'] == 'owl:AnnotationProperty':
            # Get the name of the rhombus
            rhombus_prefix = base_directive_prefix(rhombus['prefix'])
            name = rhombus_prefix + rhombus['uri']

            # Is there an arrow with the same name?
            if name in arrows_name:
                # Get the identifier of the arrows with the same name as the rhombus
                objects_identifier =  arrows_name[name]

                # Moreover, its check if its target is an uri reference
                # Iterate the identifiers
                for id in objects_identifier:

                    # Has been the arrow detected as an object property?
                    if arrows[id]['type'] == 'owl:ObjectProperty':
                        arrows[id]['type'] = 'owl:AnnotationProperty'
                    
                    # else:
                    # This case should not happen
                    
                    target = arrows[id]['target'] if 'target' in arrows[id] else ''

                    # Has the target of an annotation property been identified as a class?
                    if target in classes:
                        # Get the box
                        box = classes[target]
                        # If the box name does not have a prefix defined and its suffix is between <>,
                        # then the box reprsents an URI reference.
                        
                        # Does the box have a prefixe defined?
                        if box['prefix'] == '':
                            suffix = box['uri']

                            # Is the suffix between <>?
                            if suffix[0] == '<' and suffix[-1] == '>':
                                # The box represents an URI reference.
                                # The URI reference has been classified wrongly as a class.
                                uri_references[target] = suffix
                                del classes[target]