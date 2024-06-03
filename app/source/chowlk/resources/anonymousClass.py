from app.source.chowlk.resources.utils import base_directive_prefix
from app.source.chowlk.resources.anonymousIndividual import get_anonymous_individual

# Function to find the arrows whose source is an anonymous class or an anonymous individual (blank box).
# These blank nodes are used to construct restriction or complement triples.
def find_relations_anonymous_classes(diagram_model):
    # Get neccesary attributes
    arrows = diagram_model.get_arrows()
    anonymous_classes = diagram_model.get_anonymous_classes()
    anonymous_individuals = diagram_model.get_anonymous_individuals()

    # For each anonymous class (blank box) we want to check if there is a relation whose source is such anonymous class.
    # Iterate all the arrows.
    for relation_id, relation in arrows.items():

        # Is the arrow the source of an anonymous class?
        if relation["source"] in anonymous_classes:
            anonymous_classes[relation["source"]]["relations"].append(relation_id)
        
        # Is the arrow the source of an anonymous individual?
        elif relation["source"] in anonymous_individuals:
            anonymous_individuals[relation["source"]]["relations"].append(relation_id)

# Function to find the boxes which are below an anonymous class (blank box).
# These blank nodes are used to construct datatype properties restrictions.
def find_attributes_anonymous_classes(diagram_model):
    # Get neccesary attributes
    datatype_properties = diagram_model.get_datatype_properties()
    anonymous_classes = diagram_model.get_anonymous_classes()

    # For each anonymous class (blank box) we want to check if there is a box below such anonymous class.
    # Iterate all the datatype properties block.
    for d_p_block_id, d_p_block in datatype_properties.items():

        # Is the box below a blank box?
        if 'concept_associated' in d_p_block and d_p_block['concept_associated'] in anonymous_classes:
            anonymous_classes[d_p_block['concept_associated']]["attributes"].append(d_p_block_id)


# Function to construct a class description which represents an enumerated class.
# All the elements of a owl:oneOf must be individuals (i.e. all the elements which are connected to the hexagon
# through an arrow must be individuals).
def one_of(hexagon, individuals, diagram_model):
    anonymous_individuals = diagram_model.get_anonymous_individuals()

    # Get the identifier of the elements which are connected to the owl:oneOf hexagon.
    ids = hexagon["group"]
    text = "\n\towl:oneOf (\n"

    # Iterate the identifier of the elements which are connected to the hexagon
    for id in ids:

        # Is the element a named individual?
        if id in individuals:
            individual_prefix = base_directive_prefix(individuals[id]["prefix"])
            text += f'\t\t\t\t{individual_prefix}{individuals[id]["uri"]}\n'
        
        # Is the element an anonymous individual?
        elif id in anonymous_individuals:
            object = get_anonymous_individual(anonymous_individuals[id], anonymous_individuals, diagram_model.get_arrows(), individuals, diagram_model.get_property_values(), diagram_model)
            text += f'{object}\n'
        
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

            # Does the blank node have associated a datatype property restriction and an object property restriction?
            if anonymous_classes[id]['attributes'] and anonymous_classes[id]["relations"]:
                diagram_model.generate_error("More than one restriction is defined on the same element", id, None, "unionOf")

            # Does the blank node have associated a datatype property restriction?
            elif anonymous_classes[id]['attributes']:
                datatype_properties = diagram_model.get_datatype_properties()
                # Get the identifier of the first datatype property block which is below the blank node
                d_p_block_id = anonymous_classes[id]["attributes"][0]
                # Get the first datatype property of the first datatype property block which is below the blank node
                datatype_property = datatype_properties[d_p_block_id]['attributes'][0]
                text2, more_than_two_restrictions = datatype_property_restriction(datatype_property, diagram_model, d_p_block_id)

                if more_than_two_restrictions:
                    diagram_model.generate_error("More than one restriction is defined on the same element", id, None, "unionOf")
                
                else:
                    text = text + text2

            else:
                # In this case the blank node has associated an object property restriction
                try:
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
                        text2, more_than_two_restrictions= restrictions(complement, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes, relation_id)
                        
                        if more_than_two_restrictions:
                            diagram_model.generate_error("More than one restriction is defined on the same element", id, None, "unionOf")
                        
                        else:
                            text = text + "\t\t\t\t" + text2 + "\n"
                
                except:
                    diagram_model.generate_error("An element is not connected", id, None, "unionOf")
                
        elif not id in relations or not relations[id]["type"] == "owl:ObjectProperty":
            diagram_model.generate_error("An element of an owl:unionOf is not a class description", id, None, "unionOf")       

    text += "\t\t\t\t)"
    return text

# Function to construct a class description which represents a complement.
# All the elements of a complement must be class descriptions (i.e. all the elements which 
# are connected to the blank node through an arrow must be class descriptions).
def complement_of(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes):
    # Get the element connected to the arrow
    target_id = arrow["target"]
    text = ""

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
            text = text + union_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"

        # Is the element an intersection of class descriptions?
        elif(ellipse["type"] == "owl:intersectionOf"):
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + intersection_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"
    
    # Is the element a blank box?
    elif target_id in anonymous_classes:

        # Does the blank node have associated a datatype property restriction and an object property restriction?
        if anonymous_classes[target_id]['attributes'] and anonymous_classes[target_id]["relations"]:
            diagram_model.generate_error("More than one restriction is defined on the same element", target_id, None, "complementOf")

        # Does the blank node have associated a datatype property restriction?
        elif anonymous_classes[target_id]['attributes']:
                datatype_properties = diagram_model.get_datatype_properties()
                # Get the identifier of the first datatype property block which is below the blank node
                d_p_block_id = anonymous_classes[target_id]["attributes"][0]
                # Get the first datatype property of the first datatype property block which is below the blank node
                datatype_property = datatype_properties[d_p_block_id]['attributes'][0]
                text2, more_than_two_restrictions = datatype_property_restriction(datatype_property, diagram_model, d_p_block_id)

                if more_than_two_restrictions:
                    diagram_model.generate_error("More than one restriction is defined on the same element", target_id, None, "complementOf")
                
                else:
                    text = text + text2

        else:
            # In this case the blank node has associated a object property restriction
            try:
                # Get the identifiers of the arrows connected to the blank box
                relations_id = anonymous_classes[target_id]["relations"]
                # Get the first arrow connected to the blank box
                arrow = relations[relations_id[0]]

                # Does the arrow represent a restriction?
                if(arrow["type"] == "owl:ObjectProperty"):
                    text2, more_than_two_restrictions = restrictions(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes, relations_id[0])
                    
                    if more_than_two_restrictions:
                        diagram_model.generate_error("More than one restriction is defined on the same element", target_id, None, "complementOf")
                    
                    elif text2 != '':
                        text = text + "\t\t\t\t" + text2 + "\n"

                # Does the arrow represent a complement class description?
                elif(arrow["type"] == "owl:complementOf"):
                    # target is an anonymous class with owl:complementOf statement
                    text = text + "\n\t[ rdf:type owl:Class ;"
                    text = text + complement_of(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes)
                    text = text + "\t\t\t\t ]"
                    text = "\t\t\t\t" + text + "\n"
                
            except:
                diagram_model.generate_error("An element is not connected", target_id, None, "complementOf")

    else:
            diagram_model.generate_error("An element of an owl:complementOf is not a class description", arrow["source"], None, "complementOf")
            text = ""

    if text != "":
        text = f"\n\towl:complementOf \n{text}\t\t\t\t"

    return text

# Function to construct a class description which represents a restriction.
# All the elements of a restriction must be class descriptions (i.e. all the elements which 
# are connected to the blank node through an arrow must be class descriptions).
def restrictions(arrow, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes, arrow_id):
    text = ""
    more_than_one_restriction = False
    more_than_two_restriction = False

    # Is the arrow representing a constraint restriction?
    if (arrow["allValuesFrom"] or arrow["someValuesFrom"]) and "target" in arrow:
        
        text2, target_defined = get_restriction_target(concepts, hexagons, individuals, diagram_model, anonymous_concepts, relations, anonymous_classes, arrow["target"])

        if not target_defined:

            if arrow["allValuesFrom"]:
                diagram_model.generate_error("An all values from restriction has not a target defined", arrow_id, None, "Relations")
            
            if arrow["someValuesFrom"]:
                diagram_model.generate_error("A some values from restriction has not a target defined", arrow_id, None, "Relations")
            
            text2 = 'owl:Thing'

        if text2 != "":
            restriction_prefix = base_directive_prefix(arrow["prefix"])

            if arrow["allValuesFrom"]:
                more_than_one_restriction = True

                text = f'\n\t[ rdf:type owl:Restriction ;\n\t owl:onProperty {restriction_prefix}{arrow["uri"]};\n'\
                        f'\t owl:allValuesFrom {text2} ]'

            if arrow["someValuesFrom"]:

                if more_than_one_restriction:
                    more_than_two_restriction = True
                    text = text + ",\n"
                else:
                    more_than_one_restriction = True
                
                text = f'{text}\n\t[ rdf:type owl:Restriction ;\n\t owl:onProperty {restriction_prefix}{arrow["uri"]};\n'\
                        f'\t owl:someValuesFrom {text2} ]'
    
    # Is the arrow representing a has value restriction?
    if arrow["hasValue"]:
        # In this case the element connected to the arrow must be an individual
        target_id = arrow["target"]

        # Is the element an individual?
        if target_id in individuals:

            if more_than_one_restriction:
                more_than_two_restriction = True
                text = text + ",\n"
            else:
                more_than_one_restriction = True

            restriction_prefix = base_directive_prefix(arrow["prefix"])

            target_id = arrow["target"]
            target_prefix = base_directive_prefix(individuals[target_id]["prefix"])
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
                f'\t\t  owl:hasValue {target_prefix}{individuals[target_id]["uri"]}]'

        else:
            diagram_model.generate_error("A has value restriction has not a target defined", arrow_id, None, "Relations")

    # Is the arrow representing a minimum cardinality restriction?
    if arrow["min_cardinality"] is not None:
        if more_than_one_restriction:
            more_than_two_restriction = True
            text = text + ",\n"
        else:
            more_than_one_restriction = True

        restriction_prefix = base_directive_prefix(arrow["prefix"])

        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
            f'\t\t  owl:minCardinality \"{arrow["min_cardinality"]}\"^^xsd:nonNegativeInteger ]'

    # Is the arrow representing a maximum cardinality restriction?
    if arrow["max_cardinality"] is not None:
        if more_than_one_restriction:
            more_than_two_restriction = True
            text = text + ",\n"
        else:
            more_than_one_restriction = True

        restriction_prefix = base_directive_prefix(arrow["prefix"])
        
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
            f'\t\t  owl:maxCardinality \"{arrow["max_cardinality"]}\"^^xsd:nonNegativeInteger ]'

    # Is the arrow representing a cardinality restriction?
    if arrow["cardinality"] is not None:
        if more_than_one_restriction:
            more_than_two_restriction = True
            text = text + ",\n"
        else:
            more_than_one_restriction = True
        
        restriction_prefix = base_directive_prefix(arrow["prefix"])
        
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
            f'\t\t  owl:cardinality \"{arrow["cardinality"]}\"^^xsd:nonNegativeInteger ]'

    # Is the arrow representing a qualified restriction?
    if (arrow["max_q_cardinality"] or arrow["min_q_cardinality"] or arrow["q_cardinality"]) and "target" in arrow:
        text2, target_defined = get_restriction_target(concepts, hexagons, individuals, diagram_model, anonymous_concepts, relations, anonymous_classes, arrow["target"])

        if not target_defined:

            if arrow["max_q_cardinality"]:
                diagram_model.generate_error("A max qualified cardinality restriction has not a target defined", arrow_id, None, "Relations")
            
            if arrow["min_q_cardinality"]:
                diagram_model.generate_error("A min qualified cardinality restriction has not a target defined", arrow_id, None, "Relations")
            
            if arrow["q_cardinality"]:
                diagram_model.generate_error("A qualified cardinality restriction has not a target defined", arrow_id, None, "Relations")

            text2 = 'owl:Thing'

        if text2 != "":
            restriction_prefix = base_directive_prefix(arrow["prefix"])

            if arrow["max_q_cardinality"]:

                if more_than_one_restriction:
                    more_than_two_restriction = True
                    text = text + ",\n"
                else:
                    more_than_one_restriction = True

                text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
                        f'\t\t  owl:maxQualifiedCardinality \"{arrow["max_q_cardinality"]}\"^^xsd:nonNegativeInteger ;\n'\
                        f'\t\t owl:onClass {text2} ]'
            
            if arrow["min_q_cardinality"]:

                if more_than_one_restriction:
                    more_than_two_restriction = True
                    text = text + ",\n"
                else:
                    more_than_one_restriction = True

                text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
                        f'\t\t  owl:minQualifiedCardinality \"{arrow["min_q_cardinality"]}\"^^xsd:nonNegativeInteger ;\n'\
                        f'\t\t owl:onClass {text2} ]'
            
            if arrow["q_cardinality"]:

                if more_than_one_restriction:
                    more_than_two_restriction = True
                    text = text + ",\n"
                else:
                    more_than_one_restriction = True

                text = f'{text}\t\t[ rdf:type owl:Restriction ;\n\t\t  owl:onProperty {restriction_prefix}{arrow["uri"]} ;\n'\
                        f'\t\t  owl:qualifiedCardinality \"{arrow["q_cardinality"]}\"^^xsd:nonNegativeInteger ;\n'\
                        f'\t\t owl:onClass {text2} ]'
            
    return text, more_than_two_restriction

# Target is the identifier of the element connected to the arrow
def get_restriction_target(concepts, hexagons, individuals, diagram_model, anonymous_concepts, relations, anonymous_classes, target):
    text2 = ""
    target_defined = True
    
    # Is the element a named class?
    if target in concepts:
        text2 = named_class(concepts[target])

    # Is the element an hexagon?
    elif target in hexagons:
        hexagon = hexagons[target]

        # Is the element an enumerated class?
        if hexagon['type'] == 'owl:oneOf':
            text2 = "\n\t[ rdf:type owl:Class ;"
            text2 = text2 + one_of(hexagon, individuals, diagram_model)
            text2 = text2 + "\t\t\t\t ]"
            
    # Is the element an ellipse?
    elif target in anonymous_concepts:
        ellipse = anonymous_concepts[target]

        # Is the element an union of class descriptions?
        if(ellipse["type"] == "owl:unionOf"):
            text2 = "\n\t[ rdf:type owl:Class ;"
            text2 = text2 + union_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes)
            text2 = text2 + "\t\t\t\t ]"
            text2 = "\t\t\t\t" + text2 + "\n"
            

        # Is the element an intersection of class descriptions?
        elif(ellipse["type"] == "owl:intersectionOf"):
            text2 = "\n\t[ rdf:type owl:Class ;"
            text2 = text2 + intersection_of(ellipse, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes)
            text2 = text2 + "\t\t\t\t ]"
            text2 = "\t\t\t\t" + text2 + "\n"
    
    # Is the element a blank node?
    elif target in anonymous_classes:

        # Does the blank node have associated a datatype property restriction and an object property restriction?
        if anonymous_classes[target]['attributes'] and anonymous_classes[target]["relations"]:
            diagram_model.generate_error("Just one restriction can be defined as the target of another restriction", target, None, "Relations")

        # Does the blank node have associated a datatype property restriction?
        elif anonymous_classes[target]['attributes']:
            datatype_properties = diagram_model.get_datatype_properties()
            # Get the identifier of the first datatype property block which is below the blank node
            d_p_block_id = anonymous_classes[target]["attributes"][0]
            # Get the first datatype property of the first datatype property block which is below the blank node
            datatype_property = datatype_properties[d_p_block_id]['attributes'][0]
            text2, more_than_two_restrictions = datatype_property_restriction(datatype_property, diagram_model, d_p_block_id)

            if more_than_two_restrictions:
                diagram_model.generate_error("Just one restriction can be defined as the target of another restriction", target, None, "Relations")
                text2 = ""

        # Does the blank node have associated an object property restriction?
        elif anonymous_classes[target]["relations"]:
            try:
                # Get the identifiers of the arrows whose source is the blank node
                relations_id = anonymous_classes[target]["relations"]
                # Get the first arrow whose source is the blank node
                arrow2 = relations[relations_id[0]]

                # Does the arrow represent a restriction?
                if(arrow2["type"] == "owl:ObjectProperty"):
                    text2, more_than_two_restrictions = restrictions(arrow2, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes, relations_id[0])

                    if text2 != '':
                        text2 = "\t\t\t\t" + text2 + "\n"

                    if more_than_two_restrictions:
                        diagram_model.generate_error("Just one restriction can be defined as the target of another restriction", target, None, "Relations")
                        text2 = ""

                # Does the arrow represent a complement class description?
                elif(arrow2["type"] == "owl:complementOf"):
                    # target is an anonymous class with owl:complementOf statement
                    text2 = "\n\t[ rdf:type owl:Class ;"
                    text2 = text2 + complement_of(arrow2, concepts, diagram_model, hexagons, anonymous_concepts, individuals, relations, anonymous_classes)
                    text2 = text2 + "\t\t\t\t ]"
                    text2 = "\t\t\t\t" + text2 + "\n"

            except:
                diagram_model.generate_error("An element is not connected", target, None, "Relations")
                text2 = ""
        
        else:
            target_defined = False

    return text2, target_defined  

def datatype_property_restriction(attribute, diagram_model, block_id):
    text = ""
    more_than_one_restriction = False
    more_than_two_restriction = False
    prefix = base_directive_prefix(attribute["prefix"])

    # Is the user defining an all values from restriction?
    if attribute["allValuesFrom"]:
        more_than_one_restriction = True

        # Has the user specified a datatype?
        if attribute["uri"] and attribute["datatype"]:
            prefix_datatype = base_directive_prefix(attribute["prefix_datatype"])
            text = '\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:allValuesFrom {prefix_datatype}{attribute["datatype"]} ]\n'
        
        else:
            text = '\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:allValuesFrom owl:Thing ]\n'
            diagram_model.generate_error("An all values from restriction has not a target defined", block_id, None, "Attributes")
        

    # Is the user defining a some values from restriction?
    if attribute["someValuesFrom"]:

        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True

        # Has the user specified a datatype?
        if attribute["uri"] and attribute["datatype"]:
            prefix_datatype = base_directive_prefix(attribute["prefix_datatype"])
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:someValuesFrom {prefix_datatype}{attribute["datatype"]} ]\n'
        
        else:
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:someValuesFrom owl:Thing ]\n'
            diagram_model.generate_error("A some values from restriction has not a target defined", block_id, None, "Attributes")

    # Is the user defining a minimal cardinality restriction?
    if attribute["min_cardinality"] is not None and attribute["uri"]:
        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                f'\t\t  owl:minCardinality "{attribute["min_cardinality"]}"^^xsd:nonNegativeInteger ]\n'

    # Is the user defining a maximum cardinality restriction?
    if attribute["max_cardinality"] is not None and attribute["uri"]:
        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                f'\t\t  owl:maxCardinality "{attribute["max_cardinality"]}"^^xsd:nonNegativeInteger ]\n'

    # Is the user defining a cardinality restriction?
    if attribute["cardinality"] is not None and attribute["uri"]:
        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True
        text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                f'\t\t  owl:cardinality "{attribute["cardinality"]}"^^xsd:nonNegativeInteger ]\n'
        
    # Is the user defining a minimal qualified cardinality restriction?
    if attribute["min_q_cardinality"] is not None:

        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True

        # Has the user specified a datatype?
        if attribute["uri"] and attribute["datatype"]:
            prefix_datatype = base_directive_prefix(attribute["prefix_datatype"])
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:minQualifiedCardinality "{attribute["min_q_cardinality"]}"^^xsd:nonNegativeInteger ;\n'\
                    f'\t\t  owl:onDataRange {prefix_datatype}{attribute["datatype"]} ]\n'
        
        else:
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:minQualifiedCardinality "{attribute["min_q_cardinality"]}"^^xsd:nonNegativeInteger ;\n'\
                    f'\t\t  owl:onDataRange owl:Thing ]\n'
            diagram_model.generate_error("A min qualified cardinality restriction has not a target defined", block_id, None, "Attributes")
    
    # Is the user defining a maximal qualified cardinality restriction?
    if attribute["max_q_cardinality"] is not None:
        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True

        # Has the user specified a datatype?
        if attribute["uri"] and attribute["datatype"]:
            prefix_datatype = base_directive_prefix(attribute["prefix_datatype"])
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:maxQualifiedCardinality "{attribute["max_q_cardinality"]}"^^xsd:nonNegativeInteger ;\n'\
                    f'\t\t  owl:onDataRange {prefix_datatype}{attribute["datatype"]} ]\n'
        
        else:
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:maxQualifiedCardinality "{attribute["max_q_cardinality"]}"^^xsd:nonNegativeInteger ;\n'\
                    f'\t\t  owl:onDataRange owl:Thing ]\n'
            diagram_model.generate_error("A max qualified cardinality restriction has not a target defined", block_id, None, "Attributes")
    
    # Is the user defining a qualified cardinality restriction?
    if attribute["q_cardinality"] is not None:
        if more_than_one_restriction:
            text = f'{text},'
            more_than_two_restriction = True
        else:
            more_than_one_restriction = True

        # Has the user specified a datatype?
        if attribute["uri"] and attribute["datatype"]:
            prefix_datatype = base_directive_prefix(attribute["prefix_datatype"])
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:qualifiedCardinality "{attribute["q_cardinality"]}"^^xsd:nonNegativeInteger ;\n'\
                    f'\t\t  owl:onDataRange {prefix_datatype}{attribute["datatype"]} ]\n'
        
        else:
            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:qualifiedCardinality "{attribute["q_cardinality"]}"^^xsd:nonNegativeInteger ;\n'\
                    f'\t\t  owl:onDataRange owl:Thing ]\n'
            diagram_model.generate_error("A qualified cardinality restriction has not a target defined", block_id, None, "Attributes")

    # Is the user defining a has value restriction?
    if attribute["hasValue"]:

        if attribute["uri"] and attribute["datatype"]:
        
            if more_than_one_restriction:
                text = f'{text},'
                more_than_two_restriction = True

            # In this case the target is a data value

            # Has the user specified a datatype?
            if attribute["prefix_datatype"] == "xsd":
                # The default datatype is xsd
                aux = attribute["datatype"].split("^^")
                object = aux[0] + "^^xsd:" + aux[1]

            else:
                # In this case the user has specifyed a datatype
                object = attribute["prefix_datatype"] + ":" + attribute["datatype"]

            text = f'{text}\t\t[ rdf:type owl:Restriction ;\n'\
                    f'\t\t  owl:onProperty {prefix}{attribute["uri"]} ;\n'\
                    f'\t\t  owl:hasValue {object} ]\n'
        
        else:
            diagram_model.generate_error("A has value restriction has not a target defined", block_id, None, "Attributes")
        
    return text, more_than_two_restriction

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

            # Does the blank node have associated a datatype property restriction and an object property restriction?
            if anonymous_classes[id]['attributes'] and anonymous_classes[id]["relations"]:
                diagram_model.generate_error("More than one restriction is defined on the same element", id, None, "intersectionOf")

            # Does the blank node have associated a datatype property restriction?
            elif anonymous_classes[id]['attributes']:
                datatype_properties = diagram_model.get_datatype_properties()
                # Get the identifier of the first datatype property block which is below the blank node
                d_p_block_id = anonymous_classes[id]["attributes"][0]
                # Get the first datatype property of the first datatype property block which is below the blank node
                datatype_property = datatype_properties[d_p_block_id]['attributes'][0]
                text2, more_than_two_restrictions = datatype_property_restriction(datatype_property, diagram_model, d_p_block_id)

                if more_than_two_restrictions:
                    diagram_model.generate_error("More than one restriction is defined on the same element", id, None, "intersectionOf")
                
                else:
                    text = text + text2

            else:
                # In this case tha blank node has associated an object property restriction

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
                        text2, more_than_two_restrictions = restrictions(arrow, concepts, diagram_model, hexagons, ellipses, individuals, relations, anonymous_classes, relation_id)

                        if more_than_two_restrictions:
                            diagram_model.generate_error("More than one restriction is defined on the same element", id, None, "intersectionOf")
                        
                        else:
                            text = text + "\t\t\t\t" + text2 + "\n"
                
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