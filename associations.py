from geometry import get_corners, get_corners_rect_child

def resolve_concept_reference(attribute_blocks, concepts):
    """
    This function resolves the relative references that attribute blocks could have.
    This occur when a concept have two blocks of attributes attacked to it, i.e.
    one with domain and the other without domain. The last block have as associated concept
    the attribute block on top of it instead of the concept itself.

    :arg attribute_blocks: list of attribute blocks.
    :arg concepts: list of concepts.
    :return list of attributes with the correct associated concepts.
    """

    for attribute_block in attribute_blocks:
        concept_found = False
        source_id = attribute_block["concept_associated"]
        # Check if the object associated to this set of attributes (attribute block) is really a concept
        for concept in concepts:
            if source_id == concept["id"]:
                concept_found = True
        # If a the id was not from a concept look for the attributes associated
        # and take its concept associated
        if not concept_found:
            for attribute_block2 in attribute_blocks:
                if source_id == attribute_block2["id"]:
                    attribute_block["concept_associated"] = attribute_block2["concept_associated"]

    return attribute_blocks


def concept_attributes_association(concepts, attribute_blocks):
    associations = []

    for concept in concepts:
        associations.append({"concept": concept, "attribute_blocks": [], "relations": []})

    for attribute_block in attribute_blocks:
        concept_id = attribute_block["concept_associated"]
        for association in associations:
            if concept_id == association["concept"]["id"]:
                association["attribute_blocks"].append(attribute_block)
                break
    return associations


def concept_relations_association(associations, relations):

    for idx, relation in enumerate(relations):
        if relation["type"] == "rdf:type":
            continue
        source_id = relation["source"]
        target_id = relation["target"]
        for i, association in enumerate(associations):
            concept_id = association["concept"]["id"]
            attribute_block_ids = []
            #if len(association["attribute_blocks"]) > 0:
            for attribute_block in association["attribute_blocks"]:
                attribute_block_ids.append(attribute_block["id"])
            if source_id == concept_id or source_id in attribute_block_ids:
                association["relations"].append(relation)
                relations[idx]["source"] = concept_id
                break

        for j, association in enumerate(associations):
            concept_id = association["concept"]["id"]
            concept_prefix = association["concept"]["prefix"]
            concept_uri = association["concept"]["uri"]
            attribute_block_ids = []
            #if len(association["attribute_blocks"]) > 0:
            for attribute_block in association["attribute_blocks"]:
                attribute_block_ids.append(attribute_block["id"])
            if target_id == concept_id or target_id in attribute_block_ids:
                associations[i]["relations"][-1]["target_name"] = concept_prefix + ":" + concept_uri
                relations[idx]["target"] = concept_id

    return associations, relations

def individuals_type_identification(individuals, associations_concepts, relations):

    associations_individuals = []
    for individual in individuals:
        associations_individuals.append({"individual": individual})

    for relation in relations:
        for association in associations_individuals:
            individual_id = association["individual"]["id"]
            if relation["source"] == individual_id:
                association["relation"] = relation
                break

    for association_individual in associations_individuals:

        if association_individual["relation"]["type"] == "rdf:type":
            target_id = association_individual["relation"]["target"]
            for association_concept in associations_concepts:
                concept_id = association_concept["concept"]["id"]
                concept_prefix = association_concept["concept"]["prefix"]
                concept_uri = association_concept["concept"]["uri"]
                attribute_block_ids = []
                if len(association_concept["attribute_blocks"]) > 0:
                    for attribute_block in association_concept["attribute_blocks"]:
                        attribute_block_ids.append(attribute_block["id"])

                if target_id == concept_id or target_id in attribute_block_ids:
                    association_individual["individual"]["type"] = concept_prefix + ":" + concept_uri

        elif association_individual["relation"]["type"] == "owl:ObjectProperty":
            target_id = association_individual["relation"]["target"]
            for association_individual2 in associations_individuals:
                individual_id = association_individual2["individual"]["id"]
                individual_prefix = association_individual2["individual"]["prefix"]
                individual_uri = association_individual2["individual"]["uri"]
                if target_id == individual_id:
                    association_individual["individual"]["target_name"] = individual_prefix + ":" + individual_uri

    for association_individual in associations_individuals:
        individual = association_individual["individual"]
        if individual["type"] is None:
            geometry = individual["xml_object"][0]
            x, y = float(geometry.attrib["x"]), float(geometry.attrib["y"])
            width, height = float(geometry.attrib["width"]), float(geometry.attrib["height"])
            p1, p2, p3, p4 = get_corners(x, y, width, height)

            for association_concept in associations_concepts:
                concept = association_concept["concept"]
                geometry = concept["xml_object"][0]
                x, y = float(geometry.attrib["x"]), float(geometry.attrib["y"])
                width, height = float(geometry.attrib["width"]), float(geometry.attrib["height"])
                p1_support, p2_support, p3_support, p4_support = get_corners(x, y, width, height)
                dx = abs(p1[0] - p2_support[0])
                dy = abs(p1[1] - p2_support[1])

                if dx < 5 and dy < 5:
                    association_individual["individual"]["type"] = concept["prefix"] + ":" + concept["uri"]
                    break

    return associations_individuals


def individuals_type_identification_rdf(individuals, concepts, relations):

    relations = [relation for relation in relations if relation["type"] == "rdf:type"]

    for relation in relations:
        source_id = relation["source"]
        target_id = relation["target"]

        for individual in individuals:
            if individual["id"] == source_id:
                break
        for concept in concepts:
            if concept["id"] == target_id:
                individual["type"] = concept["prefix"] + ":" + concept["uri"]

    for individual in individuals:
        if individual["type"] is None:
            p1 = get_corners_rect_child(individual["xml_object"])[0]
            for concept in concepts:
                p2_concept = get_corners_rect_child(concept["xml_object"])[1]
                dx = abs(p1[0] - p2_concept[0])
                dy = abs(p1[1] - p2_concept[1])

                if dx < 5 and dy < 5:
                    individual["type"] = concept["prefix"] + ":" + concept["uri"]
                    break

    return individuals


def individuals_associations_rdf(individuals, relations):

    relations = [relation for relation in relations if relation["type"] == "owl:ObjectProperty"]
    associations = []
    for individual in individuals:
        associations.append({"individual": individual, "relations": []})

    for relation in relations:
        source_id = relation["source"]
        target_id = relation["target"]

        for i, association in enumerate(associations):
            if source_id == association["individual"]["id"]:
                break
        for j, association in enumerate(associations):
            if target_id == association["individual"]["id"]:
                target_name = association["individual"]["prefix"] + ":" + association["individual"]["uri"]
                relation["target_name"] = target_name
                associations[i]["relations"].append(relation)

    return associations

def individuals_attributes_associations(associations, values, relations):

    for relation in relations:
        source_id = relation["source"]
        target_id = relation["target"]

        for i, association in enumerate(associations):
            if association["individual"]["id"] == source_id:
                break
        for value in values:
            if value["id"] == target_id:
                target_name = value["value"]
                target_type = value["type"]
                relation["target_name"] = "\"" + target_name + "\"^^" + target_type
                associations[i]["relations"].append(relation)

    return associations
