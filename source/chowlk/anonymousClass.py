import tempfile

# Function to find the relations of an anonymous class (for example a restriction)
def find_relations_anonymous_classes(relations, anonimous_classes):
    # For each anonymous class we want to check if there is a relation whose source
    # is such anonymous class
    for anonimous_class_id, anonimous_class in anonimous_classes.items():

        for relation_id, relation in relations.items():

            if relation["source"] == anonimous_class_id:
                anonimous_class["relations"].append(relation_id)

    return anonimous_classes

def one_of(complement, individuals, errors):
    ids = complement["group"]
    text = "\n\towl:oneOf (\n"
    for id in ids:
        try:
            individuals_involved = individuals[id]["prefix"] + ":" + individuals[id]["uri"]
            text = text + "\t\t\t\t" + individuals_involved + "\n"
        except:
            error = {
                "message": "An element of an owl:oneOf is not an individual",
                "shape_id": id
                }
            errors["oneOf"].append(error)
    text = text + "\t\t\t\t)"
    return text

def union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes):
    ids = complement["group"]
    text = "\n\towl:unionOf ( \n"

    for id in ids:
        if id in concepts:
            # target is a class
            concepts_involved = concepts[id]["prefix"] + ":" + concepts[id]["uri"]
            text = text + "\t\t\t\t" + concepts_involved + "\n"

        elif id in hexagons:
            # target is an anonymous class with owl:oneOf statement
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + one_of(hexagons[id], individuals, errors)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"

        elif id in anonymous_concepts:
            complement = anonymous_concepts[id]

            if(complement["type"] == "owl:unionOf"):
                # target is an anonymous class with owl:unionOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

            elif(complement["type"] == "owl:intersectionOf"):
                # target is an anonymous class with owl:intersectionOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

        elif id in anonimous_classes:
            #the target is an anonymous class with owl:complementOf statement o a property restriction
            relation_id = anonimous_classes[id]["relations"][0]
            complement = relations[relation_id]
            if(complement["type"] == "owl:complementOf"):
                # target is an anonymous class with owl:complementOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

            elif (complement["type"] == "owl:ObjectProperty"):
                text = text + restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = "\t\t\t\t" + text + "\n"

        else:
            error = {
                "message": "An element of an owl:oneOf is not a class description",
                "shape_id": id
            }
            errors["unionOf"]= error

    text = text + "\t\t\t\t)"
    return text

def complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes):
    target_id = complement["target"]
    text = "\n\towl:complementOf \n"
    if target_id in concepts:
        # target is a class
        text = text + "\t\t\t\t" + concepts[target_id]["prefix"] + ":" + concepts[target_id]["uri"] + "\n"

    elif target_id in hexagons:
        # target is an anonymous class with owl:oneOf statement
        text = text + "\n\t[ rdf:type owl:Class ;"
        text = text + one_of(hexagons[target_id], individuals, errors)
        text = text + "\t\t\t\t ]"
        text = "\t\t\t\t" + text + "\n"

    elif target_id in anonymous_concepts:
        complement = anonymous_concepts[target_id]

        if(complement["type"] == "owl:unionOf"):
            # target is an anonymous class with owl:unionOf statement
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"

        elif(complement["type"] == "owl:intersectionOf"):
            # target is an anonymous class with owl:intersectionOf statement
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"
    
    elif target_id in anonimous_classes:
        complement = anonimous_classes[target_id]["relations"]
        if len(complement) > 0:
            complement = relations[complement[0]]

            if(complement["type"] == "owl:ObjectProperty"):
                text = text + restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = "\t\t\t\t" + text + "\n"

            elif(complement["type"] == "owl:complementOf"):
                # target is an anonymous class with owl:complementOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

    else:
            error = {
                "message": "An element of an owl:complementOf is not a class description",
                "shape_id": complement["source"]
            }
            errors["complementOf"].append(error)

    text = text + "\t\t\t\t"

    return text

def restrictions(restriction, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes):
    text = ""
    more_than_one_restriction = False
    if (restriction["allValuesFrom"] or restriction["someValuesFrom"]) and "target" in restriction:
        more_than_one_restriction = True
        complement = restriction["target"]
        type = "owl:allValuesFrom" if restriction["allValuesFrom"] else "owl:someValuesFrom"
        text = "\n\t[ rdf:type owl:Restriction ;"
        text = text + "\n\t owl:onProperty " + restriction["prefix"] + ":" + restriction["uri"] + " ;"
        if complement in concepts:
            # target is a class
            target = concepts[complement]["prefix"] + ":" + concepts[complement]["uri"]
            text = text + "\n\t " + type + " " + target + "]"

        elif complement in hexagons:
            # target is an anonymous class with owl:oneOf statement
            target = "\n\t[ rdf:type owl:Class ;"
            target = target + one_of(hexagons[complement], individuals, errors)
            target = target + "\t\t\t\t ]"
            text = text + "\n\t " + type + " " + target + "]"
            
        elif complement in anonymous_concepts:
            complement = anonymous_concepts[complement]

            if(complement["type"] == "owl:unionOf"):
                # target is an anonymous class with owl:unionOf statement
                target = "\n\t[ rdf:type owl:Class ;"
                target = target + union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                target = target + "\t\t\t\t ]"
                target = "\t\t\t\t" + target + "\n"
                text = text + "\n\t " + type + " " + target + "]"

            elif(complement["type"] == "owl:intersectionOf"):
                # target is an anonymous class with owl:intersectionOf statement
                target = "\n\t[ rdf:type owl:Class ;"
                target = target + intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                target = target + "\t\t\t\t ]"
                target = "\t\t\t\t" + target + "\n"
                text = text + "\n\t " + type + " " + target + "]"
        
        elif complement in anonimous_classes:
            complement = anonimous_classes[complement]["relations"]

            if len(complement) > 0:
                complement = relations[complement[0]]

                if(complement["type"] == "owl:ObjectProperty"):
                    target = restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                    target = "\t\t\t\t" + target + "\n"
                    text = text + "\n\t " + type + " " + target + "]"

                elif(complement["type"] == "owl:complementOf"):
                    # target is an anonymous class with owl:complementOf statement
                    target = "\n\t[ rdf:type owl:Class ;"
                    target = target + complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                    target = target + "\t\t\t\t ]"
                    target = "\t\t\t\t" + target + "\n"
                    text = text + "\n\t " + type + " " + target + "]"

            else:
                text = text + "]"""        

            """complement = anonimous_classes[complement]["relations"]
            if len(complement) > 0:
                print(text)
                target = restrictions(relations[complement[0]], concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                target = "\t\t\t\t" + target + "\n"
                text = text + "\n\t " + type + " " + target + "]"
            else:
                text = text + "]"""
        else:
            text = text + "]"    
    
    
    # owl:hasValue
    # The target is an individual
    if restriction["hasValue"]:
        if restriction["target"] in individuals:
            if more_than_one_restriction:
                text = text + ",\n"
            else:
                more_than_one_restriction = True
            text = text + "\t\t[ rdf:type owl:Restriction ;\n"
            text = text + "\t\t  owl:onProperty " + restriction["prefix"] + ":" + restriction["uri"] + " ;\n"
            target_id = restriction["target"]
            target_name = individuals[target_id]["prefix"] + ":" + individuals[target_id]["uri"]
            text = text + "\t\t  owl:hasValue " + target_name + " ]"

        else:
            print("error el rango de un has Value no es una instancia")

    if restriction["min_cardinality"] is not None:
        if more_than_one_restriction:
            text = text + ",\n"
        else:
            more_than_one_restriction = True 
        text = text + "\t\t[ rdf:type owl:Restriction ;\n"
        text = text + "\t\t  owl:onProperty " + restriction["prefix"] + ":" + restriction["uri"] + " ;\n"
        text = text + "\t\t  owl:minCardinality \"" + restriction["min_cardinality"] + "\"^^xsd:" + "nonNegativeInteger ]"

    if restriction["max_cardinality"] is not None:
        if more_than_one_restriction:
            text = text + ",\n"
        else:
            more_than_one_restriction = True
        text = text + "\t\t[ rdf:type owl:Restriction ;\n"
        text = text + "\t\t  owl:onProperty " + restriction["prefix"] + ":" + restriction["uri"] + " ;\n"
        text = text + "\t\t  owl:maxCardinality \"" + restriction["max_cardinality"] + "\"^^xsd:" + "nonNegativeInteger ]"

    if restriction["cardinality"] is not None:
        if more_than_one_restriction:
            text = text + ",\n"
        else:
            more_than_one_restriction = True
        text = text + "\t\t[ rdf:type owl:Restriction ;\n"
        text = text + "\t\t  owl:onProperty " + restriction["prefix"] + ":" + restriction["uri"] + " ;\n"
        text = text + "\t\t  owl:cardinality \"" + restriction["cardinality"] + "\"^^xsd:" + "nonNegativeInteger ]"

    return text

def intersection_of(intersection, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes):
    ids = intersection["group"]
    text = "\n\towl:intersectionOf ( \n"

    for id in ids:
        if id in concepts:
            # target is a class
            concepts_involved = concepts[id]["prefix"] + ":" + concepts[id]["uri"]
            text = text + "\t\t\t\t" + concepts_involved + "\n"

        elif id in hexagons:
            # target is an anonymous class with owl:oneOf statement
            text = text + "\n\t[ rdf:type owl:Class ;"
            text = text + one_of(hexagons[id], individuals, errors)
            text = text + "\t\t\t\t ]"
            text = "\t\t\t\t" + text + "\n"

        elif id in anonymous_concepts:
            complement = anonymous_concepts[id]

            if(complement["type"] == "owl:unionOf"):
                # target is an anonymous class with owl:unionOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"

            elif(complement["type"] == "owl:intersectionOf"):
                # target is an anonymous class with owl:intersectionOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"
        
        elif id in anonimous_classes:
            #the target is an anonymous class with owl:complementOf statement o a property restriction
            relation_id = anonimous_classes[id]["relations"][0]
            complement = relations[relation_id]
            if(complement["type"] == "owl:complementOf"):
                # target is an anonymous class with owl:complementOf statement
                text = text + "\n\t[ rdf:type owl:Class ;"
                text = text + complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = text + "\t\t\t\t ]"
                text = "\t\t\t\t" + text + "\n"
            elif (complement["type"] == "owl:ObjectProperty"):
                text = text + restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, relations, anonimous_classes)
                text = "\t\t\t\t" + text + "\n"

        else:
            error = {
                "message": "An element of an owl:intersectionOf is not a class description",
                "shape_id": id
            }
            errors["intersectionOf"].append(error)

    text = text + "\t\t\t\t)"
    return text