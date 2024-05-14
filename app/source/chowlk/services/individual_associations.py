from app.source.chowlk.resources.geometry import get_corners_rect_child
from app.source.chowlk.resources.utils import base_directive_prefix, create_label
from app.source.chowlk.resources.anonymousClass import intersection_of, union_of, one_of, complement_of, restrictions

# This function identify the type of each individual (i.e. the class to which they are connected).
# Individuals class membership can be declared through:
#   - An arrow which represents an rdf:type
#   - The individual is below a box which represents a named class
def individual_type_identification(diagram_model):
    # Identify the class membership through arrows
    individual_identification_arrow(diagram_model)
    # Identify the class membership through geometry, i.e. see if the individual is below a named class
    individual_identification_geometry(diagram_model)

# This function get the rdf:type arrows whose source is an individual in order to detect class membership.
# The target of the arrow must be a class description (named class or anonymous class)
def individual_identification_arrow(diagram_model):
    individuals = diagram_model.get_individuals()
    classes = diagram_model.get_classes()
    arrows = diagram_model.get_arrows()
    datatype_properties = diagram_model.get_datatype_properties()
    anonymous_concepts = diagram_model.get_ellipses()
    hexagons = diagram_model.get_hexagons()
    anonymous_classes = diagram_model.get_anonymous_classes()

    # Iterate all the arrows
    for id, relation in arrows.items():

        # Does the arrow represents an rdf:type?
        if relation["type"] != "rdf:type":
            continue

        # Get the source and target of the arrow
        source_id = relation["source"]
        target_id = relation["target"]

        # Is the source of the rdf:type arrow an individual?
        if source_id in individuals:
            individual = individuals[source_id]

            # Does the arrow represents a class membership? (i.e. the target is a named class)
            if target_id in classes:
                named_class = classes[target_id]
                prefix = base_directive_prefix(named_class["prefix"])
                individual["type"].append(f'{prefix}{named_class["uri"]}')

            # Does the arrow represents a class membership? (i.e. the target is a datatype property 
            # which is associated to a named class).
            elif target_id in datatype_properties:
                # Get the identifier of the class associated to the datatype property
                class_id = datatype_properties[target_id]["concept_associated"]

                # Is it really a class? 
                if class_id in classes:
                    named_class = classes[class_id]
                    prefix = base_directive_prefix(named_class["prefix"])
                    individual["type"].append(f'{prefix}{named_class["uri"]}')
                
                #else:
                    # The box which is on top of the attribute has not been identified as a concept.
                    # This error is derived from another error (the box above the attribute has another error),
                    # for that reason, an exception is not raise here (to avoid duplication)
            
            # Is the object an enumerated class? (i.e. owl:oneOf)
            elif target_id in hexagons:
                hexagon = hexagons[target_id]
                text = '\t[ rdf:type owl:Class ;'
                text +=  one_of(hexagon, individuals, diagram_model)
                text += "\t\t]"
                individual["type"].append(text)

            # Is the object an intersection or an union of classes? (i.e. owl:unionOf or owl:intersectionOf)
            elif target_id in anonymous_concepts:
                ellipse = anonymous_concepts[target_id]

                # Is the object an intersection of classes?
                if ellipse["type"] == "owl:intersectionOf":
                    text = '\t[ rdf:type owl:Class ;'
                    text += intersection_of(ellipse, classes, diagram_model, hexagons, anonymous_concepts, individuals, arrows, anonymous_classes)
                    text += "\t\t]"
                    individual["type"].append(text)

                # Is the object an union of classes?
                elif ellipse["type"] == "owl:unionOf":
                    text = f'\t[ rdf:type owl:Class ;'
                    text += union_of(ellipse, classes, diagram_model, hexagons, anonymous_concepts, individuals, arrows, anonymous_classes)
                    text += "\t\t]"
                    individual["type"].append(text)

            # Is the object a restriction or a complement class? (i.e. restriction or owl:complementOf)
            elif target_id in anonymous_classes:
                # In this case, the target of the arrow is a blank node which is the source of another arrow
                # (we are just interested in those arrows)
                complement_id = anonymous_classes[target_id]["relations"]
                
                # Is the blank node the source of an arrow?
                if len(complement_id) > 0:
                    # Get the arrow
                    complement = arrows[complement_id[0]]

                    # Is the object a restriction?
                    if(complement["type"] == "owl:ObjectProperty"):
                        text = '\t'
                        text += restrictions(complement, classes, diagram_model, hexagons, anonymous_concepts, individuals, arrows, anonymous_classes, complement_id[0])[0]
                        individual["type"].append(text)

                    # Is the object a complement class?
                    elif(complement["type"] == "owl:complementOf"):
                        text = '\t[ rdf:type owl:Class ;'
                        text += complement_of(complement, classes, diagram_model, hexagons, anonymous_concepts, individuals, arrows, anonymous_classes)
                        text += "\t\t]"
                        individual["type"].append(text)
            
            else:
                value = f'{base_directive_prefix(individual["prefix"])}{individual["uri"]}'
                diagram_model.generate_error("The type of an individual is not a named class", id, value, "Individual")

# This function iterate the individuals searching for boxes which are above the individual in order to detect
# class membership. In this case just named classes membership is generated.
def individual_identification_geometry(diagram_model):
    # Get the attributes from the diagram_model class
    individuals = diagram_model.get_individuals()
    classes = diagram_model.get_classes()
    boxes = diagram_model.get_boxes()
    # Dictionary whose:
    #   - key = identifier of an individual
    #   - value = named class which is on top of the individual
    individual_type = {}
    # Dictionary whose:
    #   - key = identifier of an individual
    #   - value = identifier of the individual which is above the individual which is the key
    individual_above = {}

    # Iterate all the individuals
    for ind_id, ind_below in individuals.items():
        # Get the corners (points) of the box
        p1 = get_corners_rect_child(ind_below["xml_object"])[0]
        box_found_below = True

        # Iterate all the boxes
        for box_id, box in boxes.items():
            # Get the corners (points) of the box
            p2 = box['p2']
            dx = abs(p1[0] - p2[0])
            dy = abs(p1[1] - p2[1])

            # Is the individual under a box?
            if dx < 5 and dy < 5:

                # Is that box a named class?
                if box_id in classes:
                    class_box = classes[box_id]
                    # Add class membership
                    name = f'{base_directive_prefix(class_box["prefix"])}{class_box["uri"]}'
                    ind_below["type"].append(name)
                    individual_type[ind_id] = name
                    # A box just can be under another box
                    box_found_below = False
                
                else:
                    value = f'{base_directive_prefix(ind_below["prefix"])}{ind_below["uri"]}'
                    diagram_model.generate_error("An individual is below an element that is not a named class", ind_id, value, "Individual")

                break
        
        # Is not the individual under another box?
        if box_found_below:

            # Iterate all the individuals
            for ind_id_2, individual_2 in individuals.items():

                # Skip same elements
                if ind_id == ind_id_2:
                    continue

                p2 = get_corners_rect_child(individual_2["xml_object"])[1]
                dx = abs(p1[0] - p2[0])
                dy = abs(p1[1] - p2[1])

                # Is the individual under another individual (individual above)?
                if dx < 5 and dy < 5:

                    # Is that individual (individual above) under a named class?
                    if ind_id_2 in individual_type:
                        # Get the name of the class which is on top
                        name = individual_type[ind_id_2]
                        # Add the type to the individual
                        ind_below["type"].append(name)
                        # Store the name of the class which is on top
                        individual_type[ind_id] = name

                    else:
                        # In this case we dont know yet the name of the class which is on top of the tower.
                        # We stored that the type of the individual must be equal to the type of the individual above.
                        individual_above[ind_id] = ind_id_2

                    break

    # Iterate all the individuals (whose type we dont know yet) which are under another individual
    for ind_below_id, ind_above_id in individual_above.items():
        ind_below = individuals[ind_below_id]

        # Has the type of the above individual been identified yet?
        if ind_above_id in individual_type:
            ind_below['type'].append(individual_type[ind_above_id])

        # Has the type of the above individual not been identified yet?
        elif ind_above_id in individual_above:

            
            try:
                 # It is neccesary to identify the type of the above individual
                 class_id = get_class_above(individual_type, individual_above, individual_above[ind_above_id])
                 ind_below['type'].append(class_id)
                 individual_type[ind_below_id] = class_id
            
            except:
                value = f'{base_directive_prefix(ind_below["prefix"])}{ind_below["uri"]}'
                diagram_model.generate_error("An individual is below an element that is not a named class", ind_below_id, value, "Individual")
        
        else:
            value = f'{base_directive_prefix(ind_below["prefix"])}{ind_below["uri"]}'
            diagram_model.generate_error("An individual is below an element that is not a named class", ind_below_id, value, "Individual")

# This function update the identifier of the class which is on top of a tower of individuals.
def get_class_above(individual_type, individual_above, ind_below_id):

    # Has the type of the above individual been identified yet?
    if ind_below_id in individual_type:
        return individual_type[ind_below_id]
    
    # Has the type of the above individual not been identified yet?
    elif ind_below_id in individual_above:
        return get_class_above(individual_type, individual_above, individual_above[ind_below_id])
    
    else:
        # This should not happen.
        raise Exception("Invalid element above an individual")


def individual_relation_association(diagram_model):

    individuals = diagram_model.get_individuals()
    arrows = diagram_model.get_arrows()
    anonymous_individuals = diagram_model.get_anonymous_individuals()

    # Variable to store per named individual the arrows whose source is that individual
    associations = {}

    # Fill the variable associations with empty values
    for id, individual in individuals.items():
        associations[id] = {"individual": individual,
                            "relations": {}, "attributes": {}}
        
    # Iterate all the arrows
    for relation_id, relation in arrows.items():

        # Has been the arrow identified as an object property?
        if relation["type"] == "owl:ObjectProperty":
            # Get the source of the arrow
            source_id = relation["source"]
            # Get the target of the arrow
            target_id = relation["target"]

            # Is the source of the arrow a named individual and the target a named/anonymous individual?
            if source_id in associations and (target_id in individuals or target_id in anonymous_individuals):
                association = associations[source_id]
                association["relations"][relation_id] = relation

        # Has been the arrow identified as an owl:sameAs?
        elif relation["type"] == "owl:sameAs":
            # Get the source of the arrow
            source_id = relation["source"]
            # Get the target of the arrow
            target_id = relation["target"]

            # Is the source of the arrow a named individual and the target a named/anonymous individual?
            if source_id in associations and (target_id in individuals or target_id in anonymous_individuals):
                association = associations[source_id]
                association["relations"][relation_id] = relation
                association["relations"][relation_id]["prefix"] = "owl"
                association["relations"][relation_id]["uri"] = "sameAs"

        # Has been the arrow identified as an owl:differentFrom?
        elif relation["type"] == "owl:differentFrom":
            # Get the source of the arrow
            source_id = relation["source"]
            # Get the target of the arrow
            target_id = relation["target"]

            # Is the source of the arrow a named individual and the target a named/anonymous individual?
            if source_id in associations and (target_id in individuals or target_id in anonymous_individuals):
                association = associations[source_id]
                association["relations"][relation_id] = relation
                association["relations"][relation_id]["prefix"] = "owl"
                association["relations"][relation_id]["uri"] = "differentFrom"

        # Has been the arrow identified as an annotation property?
        elif relation["type"] == 'owl:AnnotationProperty':
            # Get the source of the arrow
            source_id = relation["source"]
            # Get the target of the arrow
            target_id = relation["target"]

            # Is the source of the arrow a named individual?
            if source_id in associations:
                association = associations[source_id]
                association["relations"][relation_id] = relation

    return associations

# This function create a new datatype property which is declared though an arrow.
# In this case the arrow has been used in order to declare a triple (individual datatypeProperty dataValue).
def add_datatype_property(arrow_id, arrow, attribute_blocks):
    
        attribute = {}
        attribute_block = {}
        attribute_block["xml_object"] = arrow['xml_object']
        attribute["prefix"] = arrow['prefix']
        attribute["uri"] = arrow['uri']
        attribute["label"] = create_label(arrow['prefix'], arrow['uri'], "property")
        attribute["datatype"] = None
        attribute["functional"] = False
        attribute["domain"] = False
        attribute["range"] = False
        attribute["allValuesFrom"] = False
        attribute["someValuesFrom"] = False
        attribute["hasValue"] = False
        attribute["min_cardinality"] = None
        attribute["max_cardinality"] = None
        attribute['deprecated'] = arrow['deprecated']
        attribute_block["attributes"] = [attribute]

        attribute_blocks[arrow_id] = attribute_block

# This function identify the arrows which represents a datatype property.
# These arrows are characterised by being misclassified as object properties, leaving from an individual and ending at a data value.
def individual_attribute_association(associations, diagram_model):
    # Get the attributes from the model
    property_values = diagram_model.get_property_values()
    arrows = diagram_model.get_arrows()
    datatype_properties = diagram_model.get_datatype_properties()
    anonymous_individuals = diagram_model.get_anonymous_individuals()

    # Iterate all the arrows
    for relation_id, relation in arrows.items():
        # Get the source and target of the arrow
        source_id = relation["source"]
        target_id = relation["target"]

        # Has the arrow been identified as an annotation property?
        if 'type' in relation and relation['type'] == 'owl:AnnotationProperty':
            # The arrow is not misclassified (it does not have to be identified as a datatype property)
            continue

        # Is the source of the arrow a named individual and the target a data value?
        if target_id in property_values and source_id in associations:
            # Change the type of the arrow (it has been misclasified as an object property)
            relation["type"] = "owl:DatatypeProperty"
            association = associations[source_id]
            # Store that the individual is the subject of a triple (individual datatypeProperty dataValue)
            association["attributes"][relation_id] = relation

            # Create datatype property declaration
            add_datatype_property(relation_id, relation, datatype_properties)

        # Is the source of the arrow an anonymous individual and the target a data value?
        elif target_id in property_values and source_id in anonymous_individuals:
            # Change the type of the arrow (it has been misclasified as an object property)
            relation["type"] = "owl:DatatypeProperty"
            # Create datatype property declaration
            add_datatype_property(relation_id, relation, datatype_properties)
                
    return associations

# This function update the information of the arrows which are connected to a datatype property. Precisely if the arrow is connected 
# to a datatype property, this function replace the target or the source (depending of the edge of the arrow) for the concept 
# associated to the datatype property.
def datatype_relation_association(diagram_model):
    # Get the attributes from the diagram model
    arrows = diagram_model.get_arrows()
    datatype_properties = diagram_model.get_datatype_properties()

    # Iterate all the arrows
    for arrow_id, arrow in arrows.items():

        # Is the arrow connected to a datatype property (target)?
        if 'target' in arrow and arrow['target'] in datatype_properties:
            # Get the datatype property
            datatypeProperty = datatype_properties[arrow['target']]

            # Is the datatype property connected to a class?
            if 'concept_associated' in datatypeProperty:
                # Change the datatype property by its associated concept
                arrow['target'] = datatypeProperty['concept_associated']
        
        # Is the arrow connected to a datatype property (target)?
        if 'source' in arrow and arrow['source'] in datatype_properties:
            # Get the datatype property
            datatypeProperty = datatype_properties[arrow['source']]

            # Is the datatype property connected to a class?
            if 'concept_associated' in datatypeProperty:
                # Change the datatype property by its associated concept
                arrow['source'] = datatypeProperty['concept_associated']
