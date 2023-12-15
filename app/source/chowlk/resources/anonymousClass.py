from app.source.chowlk.resources.utils import base_directive_prefix

# Function to find the arrows whose source is an anonymous class (blank box).
# These blank nodes are used to construct restriction or complement triples.
def find_relations_anonymous_classes(diagram_model):
    # Get neccesary attributes
    arrows = diagram_model.get_arrows()
    anonymous_classes = diagram_model.get_anonymous_classes()

    # For each anonymous class (blank box) we want to check if there is a relation whose source is such anonymous class.
    # Iterate all the arrows.
    for relation_id, relation in arrows.items():

        # Is the arrow the source of a blank box?
        if relation["source"] in anonymous_classes:
            anonymous_classes[relation["source"]]["relations"].append(relation_id)

# Function to construct a class description which represents an enumerated class.
# All the elements of a owl:oneOf must be individuals (i.e. all the elements which are connected to the hexagon
# through an arrow must be individuals).
def one_of(hexagon, individuals, diagram_model):
    # Get the identifier of the elements which are connected to the owl:oneOf hexagon.
    ids = hexagon["group"]
    text = "\n\towl:oneOf (\n"

    # Iterate the identifier of the elements which are connected to the hexagon
    for id in ids:

        # Is the element an individual?
        if id in individuals:
            individual_prefix = base_directive_prefix(individuals[id]["prefix"])
            text += f'\t\t\t\t{individual_prefix}{individuals[id]["uri"]}\n'
        
        else:
            diagram_model.generate_error("An element of an owl:oneOf is not an individual", id, None, "oneOf")

    text += "\t\t\t\t)"
    return text

# Function to construct a class description which represents an union of class descriptions.
# All the elements of a owl:unionOf must be class descriptions (i.e. all the elements which 
# are connected to the ellipse through an arrow must be class descriptions).
def union_of(complement, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes):
    # Get the identifiers of the elements connected to the owl:unionOf ellipse
    ids = complement["group"]
    text = "\n\towl:unionOf ( \n"

    # Iterate the identifiers of the elements connected to the owl:unionOf ellipse
    for id in ids:
        
        # Is the element a named class?
        if id in concepts:
            text += named_class(concepts[id])

        # Is the element an hexagon?
        elif id in hexagons:
            hexagon = hexagons[id]

            # Is the element an enumerated class?
            if hexagon['type'] == "owl:oneOf":
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + one_of(hexagons[id], individuals, diagram_model)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

        # Is the element an ellipse?
        elif id in ellipses:
            ellipse = ellipses[id]

            # Is the element an union of class descriptions?
            if(ellipse["type"] == "owl:unionOf"):
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + union_of(ellipse, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

            # Is the element an intersection of class descriptions?
            elif(ellipse["type"] == "owl:intersectionOf"):
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + intersection_of(ellipse, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

        # Is the element a blank box?
        elif id in anonymous_classes:
            # Get the identifier of the first arrow whose source is the blank node
            relation_id = anonymous_classes[id]["relations"][0]
            # Get the first arrow whose source is the blank node
            complement = relations[relation_id]

            # Does the arrow represent a complement class description?
            if(complement["type"] == "owl:complementOf"):
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + complement_of(complement, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

            # Does the arrow represent a restriction?
            elif (complement["type"] == "owl:ObjectProperty"):
                text = text + restrictions(complement, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                text = "\t\t\t\t" + text + "\n"
  
        elif not id in relations or not relations[id]["type"] == "owl:ObjectProperty":
            diagram_model.generate_error("An element of an owl:unionOf is not a class description", id, None, "unionOf")       

    text += "\t\t\t\t)"
    return text

# Function to construct a class description which represents a complement.
# All the elements of a complement must be class descriptions (i.e. all the elements which 
# are connected to the blank node through an arrow must be class descriptions).
def complement_of(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes):
    # Get the element connected to the arrow
    target_id = arrow["target"]
    text = "\n\towl:complementOf \n"

    # Is the element a class?
    if target_id in concepts:
        text += named_class(concepts[target_id])

    # Is the element an hexagon?
    elif target_id in hexagons:
        hexagon = hexagons[target_id]

        # Is the element an enumerated class?
        if hexagon['type'] == 'owl:oneOf':
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + one_of(hexagon, individuals, diagram_model)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"

    # Is the element an ellipse?
    elif target_id in anonymous_concepts:
        ellipse = anonymous_concepts[target_id]

        # Is the element an union of class descriptions?
        if(ellipse["type"] == "owl:unionOf"):
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + union_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"

        # Is the element an intersection of class descriptions?
        elif(ellipse["type"] == "owl:intersectionOf"):
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + intersection_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"
    
    # Is the element a blank box?
    elif target_id in anonimous_classes:

        # Get the identifiers of the arrows connected to the blank box
        relations_id = anonimous_classes[target_id]["relations"]

        if len(relations_id) > 0:
            # Get the first arrow connected to the blank box
            arrow = relations[relations_id[0]]

            # Does the arrow represent a restriction?
            if(arrow["type"] == "owl:ObjectProperty"):
                text = text + restrictions(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = "\t\t\t\t" + text + "\n"

            # Does the arrow represent a complement class description?
            elif(arrow["type"] == "owl:complementOf"):
                # target is an anonymous class with owl:complementOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + complement_of(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

    else:
            diagram_model.generate_error("An element of an owl:complementOf is not a class description", arrow["source"], None, "complementOf")
            text = ""

    text = text + "\t\t\t\t"

    return text

# Function to construct a class description which represents a restriction.
# All the elements of a restriction must be class descriptions (i.e. all the elements which 
# are connected to the blank node through an arrow must be class descriptions).
def restrictions(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes):
    text = ""
    more_than_one_restriction = False

    # Is the arrow representing a constraint restriction?
    if (arrow["allValuesFrom"] or arrow["someValuesFrom"]) and "target" in arrow:
        more_than_one_restriction = True
        # Get the identifier of the element connected to the arrow
        target = arrow["target"]
        type = "owl:allValuesFrom" if arrow["allValuesFrom"] else "owl:someValuesFrom"
        restriction_prefix = base_directive_prefix(arrow["prefix"])
        text = f'\n\t[ rdf:type owl:Restriction ;\n\t owl:onProperty {restriction_prefix}{arrow["uri"]};'

        # Is the element a named class?
        if target in concepts:
            text2 = named_class(concepts[target])
            text = text + "\n\t " + type + " " + text2 + "]"

        # Is the element an hexagon?
        elif target in hexagons:
            hexagon = hexagons[target]

            # Is the element an enumerated class?
            if hexagon['type'] == 'owl:oneOf':
                text2 = "\n\t[ rdf:type owl:Class ;"
                text2 = text2 + one_of(hexagon, individuals, diagram_model)
                text2 = text2 + "\t\t\t\t ]"
                text = text + "\n\t " + type + " " + text2 + "]"
        
        # Is the element an ellipse?
        elif target in anonymous_concepts:
            ellipse = anonymous_concepts[target]

            # Is the element an union of class descriptions?
            if(ellipse["type"] == "owl:unionOf"):
                text2 = "\n\t[ rdf:type owl:Class ;"
                text2 = text2 + union_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text2 = text2 + "\t\t\t\t ]"
                text2 = "\t\t\t\t" + text2 + "\n"
                text = text + "\n\t " + type + " " + text2 + "]"

            # Is the element an intersection of class descriptions?
            elif(ellipse["type"] == "owl:intersectionOf"):
                text2 = "\n\t[ rdf:type owl:Class ;"
                text2 = text2 + intersection_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text2 = text2 + "\t\t\t\t ]"
                text2 = "\t\t\t\t" + text2 + "\n"
                text = text + "\n\t " + type + " " + text2 + "]"
        
        # Is the element a blank node?
        elif target in anonimous_classes:

            # Get the identifiers of the arrows whose source is the blank node
            relations_id = anonimous_classes[target]["relations"]

            if len(relations_id) > 0:
                # Get the first arrow whose source is the blank node
                arrow2 = relations[relations_id[0]]

                # Does the arrow represent a restriction?
                if(arrow2["type"] == "owl:ObjectProperty"):
                    target = restrictions(arrow2, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                    target = "\t\t\t\t" + target + "\n"
                    text = text + "\n\t " + type + " " + target + "]"

                # Does the arrow represent a complement class description?
                elif(arrow2["type"] == "owl:complementOf"):
                    # target is an anonymous class with owl:complementOf statement
                    target = "\n\t[ rdf:type owl:Class ;"
                    target = target + complement_of(arrow2, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                    target = target + "\t\t\t\t ]"
                    target = "\t\t\t\t" + target + "\n"
                    text = text + "\n\t " + type + " " + target + "]"

            else:
                text = ""      

        else:
            text = ""    
    
    # Is the arrow representing a has value restriction?
    if arrow["hasValue"]:
        # In this case the element connected to the arrow must be an individual
        target_id = arrow["target"]

        # Is the element an individual?
        if target_id in individuals:

            if more_than_one_restriction:
                text = text + ",\n"
            else:
                more_than_one_restriction = True

            restriction_prefix = base_directive_prefix(arrow["prefix"])

            target_id = arrow["target"]
            target_prefix = base_directive_prefix(individuals[target_id]["prefix"])
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
                f'\t\t  owl:hasValue {target_prefix}{individuals[target_id]["uri"]}]'

        else:
            print("error el rango de un has Value no es una instancia")

    # Is the arrow representing a minimum cardinality restriction?
    if arrow["min_cardinality"] is not None:
        if more_than_one_restriction:
            text = text + ",\n"
        else:
            more_than_one_restriction = True

        restriction_prefix = base_directive_prefix(arrow["prefix"])

        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
            f'\t\t  owl:minCardinality \"{arrow["min_cardinality"]}\"^^xsd:nonNegativeInteger ]'

    # Is the arrow representing a maximum cardinality restriction?
    if arrow["max_cardinality"] is not None:
        if more_than_one_restriction:
            text = text + ",\n"
        else:
            more_than_one_restriction = True

        restriction_prefix = base_directive_prefix(arrow["prefix"])
        
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
            f'\t\t  owl:maxCardinality \"{arrow["max_cardinality"]}\"^^xsd:nonNegativeInteger ]'

    # Is the arrow representing a cardinality restriction?
    if arrow["cardinality"] is not None:
        if more_than_one_restriction:
            text = text + ",\n"
        else:
            more_than_one_restriction = True
        
        restriction_prefix = base_directive_prefix(arrow["prefix"])
        
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
            f'\t\t  owl:cardinality \"{arrow["cardinality"]}\"^^xsd:nonNegativeInteger ]'

    return text

# Function to construct a class description which represents an intersection of class descriptions.
# All the elements of a owl:intersectionOf must be class descriptions (i.e. all the elements which 
# are connected to the ellipse through an arrow must be class descriptions).
def intersection_of(intersection, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes):
    # Get the identifier of the elements connected to the owl:intersectionOf ellipse
    ids = intersection["group"]
    text = "\n\towl:intersectionOf ( \n"

    # Iterate the identifiers of the elements connected to the owl:intersectionOf ellipse
    for id in ids:

        # Is the element a named class?
        if id in concepts:
            text += named_class(concepts[id])
        
        # Is the element an hexagon?
        elif id in hexagons:
            hexagon = hexagons[id]

            # Is the element an enumerated class?
            if hexagon['type'] == "owl:oneOf":
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + one_of(hexagon, individuals, diagram_model)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

        # Is the element an ellipse?
        elif id in ellipses:
            ellipse = ellipses[id]

            # Is the element an union of class descriptions?
            if(ellipse["type"] == "owl:unionOf"):
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + union_of(ellipse, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

            # Is the element an intersection of class descriptions?
            elif(ellipse["type"] == "owl:intersectionOf"):
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + intersection_of(ellipse, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"
        
        # Is the element a blank node?
        elif id in anonymous_classes:

            try:
                # Get the identifier of the first arrow whose source is the blank node
                relation_id = anonymous_classes[id]["relations"][0]
                # Get the first arrow whose source is the blank node
                arrow = relations[relation_id]

                # Does the arrow represent an owl:complementOf?
                if(arrow["type"] == "owl:complementOf"):
                    text = text + "\n\t[ rdf:type owl:Class ;"
                    text = text + complement_of(arrow, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                    text = text + "\t\t\t\t ]"
                    text = "\t\t\t\t" + text + "\n"

                # Does the arrow represent a restriction?
                elif (arrow["type"] == "owl:ObjectProperty"):
                    text = text + restrictions(arrow, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes)
                    text = "\t\t\t\t" + text + "\n"
            
            except:
                diagram_model.generate_error("An element is not connected", id, None, "intersectionOf")
        

        elif not id in relations or not relations[id]["type"] == "owl:ObjectProperty":
            diagram_model.generate_error("An element of an owl:intersectionOf is not a class description", id, "No value", "intersectionOf")

    text = text + "\t\t\t\t)"
    return text

# Function to gte the name of a named class
def named_class(concept):
    concept_prefix = base_directive_prefix(concept["prefix"])
    return f'\t\t\t\t{concept_prefix}{concept["uri"]}\n'