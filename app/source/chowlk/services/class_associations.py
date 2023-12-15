# This function resolves the relative references that attribute blocks could have.
# This occur when a concept have more than one block of attributes attacked to it. Each block (except the first) 
# have as associated concept the attribute block above of it instead of the concept which is on top of the tower of blocks.
def resolve_concept_reference(diagram_model):
    # Get th attributes from the diagram model
    datatype_properties = diagram_model.get_datatype_properties()
    classes = diagram_model.get_classes()

    # Iterate all the datatype properties blocks
    for property_id, property_block in datatype_properties.items():

        # Is the block below another box?
        if "concept_associated" not in property_block:
            continue

        # Get the identifier of the box which is above the datatype block
        above_box_id = property_block["concept_associated"]

        # Is the box another datatype property block?
        if above_box_id in datatype_properties:
            # In this case the identifier from a datatype property block is stored, but it is neccesary to store
            # the identifier of the class which is on top of all the datatype property blocks.
            try:
                class_id = update_class_associated(above_box_id, datatype_properties, classes)
                property_block["concept_associated"] = class_id
                update_domain(property_block, class_id)
            
            except:
                diagram_model.generate_error("Datatype property block not attached to a named class", property_id, None, "Attributes")

# This function update the identifier of the class which is on top of a tower of datatype property blocks.
# The recursive function is going through the tower until it finds a datatype property which correctly stores 
# the identifier of a class. Then it updates all the property blocks it has gone through.
def update_class_associated(above_box_id, datatype_properties, classes):

    # Is the above box a class?
    if above_box_id in classes:
        # Already up to date
        class_id = above_box_id
    
    # Is the above box a datatype property box?
    elif above_box_id in datatype_properties:
        # In this case the identifier from a datatype property block is stored, but it is neccesary to store
        # the identifier of the class which is on top of all the datatype property blocks.
        property_block = datatype_properties[above_box_id]
        class_id = update_class_associated(property_block["concept_associated"], datatype_properties, classes)
        # Update the identifier of the class which is on top of all the datatype property blocks.
        property_block["concept_associated"] = class_id
        update_domain(property_block, class_id)
    
    else:
        # This should not happen.
        raise Exception("Invalid element above a datatype property block")
    
    return class_id

# This function update the domain of all the datatype properties which are defined in a datatype property
# block which is below another datatype property block. class_id store the identifier of the class which 
# is on top of all the datatype property blocks.
def update_domain(property_block, class_id):

    # Iterate all the datatype properties which are defined inside the block
    for datatype_property in property_block["attributes"]:

        # Has the datatype property got define a domain?
        if datatype_property["domain"] != False:
            # Update the identifier of the domain
            datatype_property["domain"] = class_id

# This function create a map called association in which the following information is going to be stored:
# - The named classes
# - The datatype properties which are connected to those named classes
# - The arrows which comes from those named classes
# Moreover, this function fills the map whith the datatype properties connected to the named classes.
def concept_attribute_association(diagram_model):
    # Get neccesary attributes from the model
    classes = diagram_model.get_classes()
    datatype_properties = diagram_model.get_datatype_properties()
    # Map to srore the connections of the named classes
    associations = {}

    # Iterate all the classes
    for id, concept in classes.items():
        # Create the structure of the map for each named class
        associations[id] = {"concept": concept,
                            "attribute_blocks": {}, 
                            "relations": {}}

    # Iterate all the datatype property blocks
    for id, datatype_property_block in datatype_properties.items():

        # Is the datatype property block connected to a named class?
        if "concept_associated" in datatype_property_block:
            # Get the class identifier
            class_id = datatype_property_block["concept_associated"]

            # Is it really a class?
            if class_id in associations:
                # Add that the class is connected to the datatype property
                associations[class_id]["attribute_blocks"][id] = datatype_property_block

    return associations

# This function fills the "associations" map with the arrows which comes from a named class.
def concept_relation_association(associations, diagram_model):
    # Get neccesary attributes from the model
    arrows = diagram_model.get_arrows()

    # Iterate all the arrows
    for arrow_id, arrow in arrows.items():
        # Get the type of the arrow
        type = arrow["type"] if "type" in arrow else None

        # Is an arrow a special arrow?
        if type in ["ellipse_connection", "rdfs:range", "rdfs:domain"]:
            continue

        # Get the source and target of the arrow
        source_id = arrow["source"]
        target_id = arrow["target"]

        if source_id is None or target_id is None:
            continue

        for s_concept_id, association in associations.items():
            if source_id == s_concept_id or source_id in association["attribute_blocks"]:
                associations[s_concept_id]["relations"][arrow_id] = arrow
                arrows[arrow_id]["source"] = s_concept_id

                for t_concept_id, association in associations.items():
                    if target_id == t_concept_id or target_id in association["attribute_blocks"]:
                        associations[s_concept_id]["relations"][arrow_id]["target"] = t_concept_id
                        arrows[arrow_id]["target"] = t_concept_id
                        break

    return associations