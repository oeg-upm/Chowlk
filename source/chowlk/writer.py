import tempfile
from source.chowlk.anonymousClass import *

def get_ttl_template(namespaces, prefixes_fonded, errors):

    file = tempfile.TemporaryFile(mode='w+', encoding="utf-8")

    #file = open(filename, 'w', encoding="utf-8")

    file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
               "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
               "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
               "@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n"
               "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
               "@prefix dc: <http://purl.org/dc/elements/1.1/> .\n"
               "@prefix dcterms: <http://purl.org/dc/terms/> .\n"
               "@prefix vann: <http://purl.org/vocab/vann/> .\n")

    not_found = []
    for prefix in prefixes_fonded:
        if prefix not in namespaces:
            not_found.append(prefix)

    default_uri = "http://www.owl-ontologies.com/{}#"
    new_namespaces = dict()

    for ns in not_found:
        if(ns != "" and ns != "<cambiar_a_base" and ns != "cambiar_a_prefijo_vacio"):
            new_namespaces[ns] = default_uri.format(ns)

    if len(namespaces) == 0:
        onto_prefix = list(new_namespaces.keys())[0]
        onto_uri = new_namespaces[onto_prefix]
    else:
        onto_prefix = list(namespaces.keys())[0]
        onto_uri = namespaces[onto_prefix]

    empty_prefix_declared = True
    base_declared = True
    prefixes = []
    for prefix, uri in namespaces.items():
        if(prefix == ""):
            empty_prefix_declared = False
        if(prefix == "base"):
            base_declared = False
            onto_uri = uri
            onto_prefix = prefix
        else:
            prefixes.append("@prefix " + prefix + ": <" + uri + "> .\n")

    if(base_declared):
        errors["Base"] = {
            "message": "A base has not been declared. The first namespace has been taken as base"
        }

    #Add empty prefix with same uri as @base if the user has not declared the
    #empty prefix in namespace (the empty prefix has to be above the other prefixes
    # because of rdflib)
    if(empty_prefix_declared):
        file.write("@prefix : <" + onto_uri + "> .\n")

    for prefix in prefixes:
        file.write(prefix)

    for prefix, uri in new_namespaces.items():
        file.write("@prefix " + prefix + ": <" + uri + "> .\n")

    file.write("@base <" + onto_uri + "> .\n\n")

    return file, onto_prefix, onto_uri, new_namespaces, errors

def write_ontology_metadata(file, metadata, onto_uri):

    file.write("<" + onto_uri + "> rdf:type owl:Ontology")
    for prefix, values in metadata.items():

        for value in values:
            file.write(" ;\n")
            if "imports" in prefix:
                file.write("\t\t\t" + prefix + " " + "<" + value + ">")
            else:
                value = "\"" + value + "\""
                file.write("\t\t\t" + prefix + " " + value)
    file.write(" ;\n")
    file.write("\t\t\t" + "dc:description \"Ontology code created by Chowlk\"")
    file.write(" .\n\n")

    return file


def write_object_properties(file, relations, concepts, anonymous_concepts, attribute_blocks, hexagons, individuals, errors):

    file.write("#################################################################\n"
               "#    Object Properties\n"
               "#################################################################\n\n")

    for relation_id, relation in relations.items():
        if "type" not in relation:
            continue

        if relation["type"] == "owl:ObjectProperty":
            uri = relation["uri"]
            prefix = relation["prefix"]

            file.write("### " + prefix + ":" + uri + "\n")
            file.write(prefix + ":" + uri + " rdf:type owl:ObjectProperty")
            if relation["functional"]:
                file.write(" ,\n")
                file.write("\t\t\towl:FunctionalProperty")

            if relation["symmetric"]:
                file.write(" ,\n")
                file.write("\t\t\towl:SymmetricProperty")

            if relation["transitive"]:
                file.write(" ,\n")
                file.write("\t\t\towl:TransitiveProperty")

            if relation["inverse_functional"]:
                file.write(" ,\n")
                file.write("\t\t\towl:InverseFunctionalProperty")

            if relation["domain"]:
                concept_id = relation["domain"]

                if concept_id in concepts:
                    concept = concepts[concept_id]
                    domain_name = concept["prefix"] + ":" + concept["uri"]

                elif concept_id in attribute_blocks:
                    concept_id = attribute_blocks[concept_id]["concept_associated"]
                    concept = concepts[concept_id]
                    domain_name = concept["prefix"] + ":" + concept["uri"]

                # domain owl:oneOf
                elif relation["domain"] in hexagons:
                    target_id = relation["domain"]
                    complement = hexagons[target_id]
                    domain_name = "[ rdf:type owl:Class ;"
                    domain_name = domain_name +  one_of(complement, individuals, {}) 
                    domain_name = domain_name + "\t\t]"  

                elif relation["domain"] in individuals:
                    error = {
                        "message": "The domain of an object property is an individual",
                        "shape_id": relation_id,
                        "value": prefix + ":" + uri
                    }
                    errors["objectProperty_domain"]= error
                    domain_name = ":"
                
                else:
                    domain_name = ":"

                # Avoid blank nodes
                if domain_name != ":":
                    file.write(" ;\n")
                    file.write("\t\trdfs:domain " + domain_name)

            #has value restrictions do not have range
            if relation["range"] and not relation["hasValue"]:
                if "range" in relation and relation["range"] in concepts:
                    concept_id = relation["range"]
                    concept = concepts[concept_id]
                    range_name = concept["prefix"] + ":" + concept["uri"]
                    file.write(" ;\n")
                    file.write("\t\trdfs:range " + range_name)
                
                elif relation["range"] in individuals:
                    error = {
                        "message": "The range of an object property is an individual",
                        "shape_id": relation_id,
                        "value": prefix + ":" + uri
                    }
                    errors["objectProperty_range"]= error

                # range owl:oneOf
                # For the moment is disabled
                """elif  relation["range"] in hexagons:
                    target_id = relation["range"]
                    complement = hexagons[target_id]
                    file.write(" ; \n")
                    file.write("\t\trdfs:range [ rdf:type owl:Class ;")
                    text =  one_of(complement, individuals, {})
                    file.write(text)
                    file.write("\t\t]")"""  

                #For the moment is disabled
                """else:
                    blank_id = relation["target"]
                    if blank_id in anonymous_concepts:
                        group_node = anonymous_concepts[blank_id]
                        try:
                            concept_ids = group_node["group"]
                            concept_names = [concepts[id]["prefix"] + ":" + concepts[id]["uri"] for id in concept_ids]
                            file.write(" ;\n")
                            file.write("\t\trdfs:range [ " + group_node["type"] + " ( \n")
                            for name in concept_names:
                                file.write("\t\t\t\t\t\t" + name + "\n")

                            file.write("\t\t\t\t\t) ;\n")
                            file.write("\t\t\t\t\trdf:type owl:Class\n")
                            file.write("\t\t\t\t\t]")
                        except:
                            print("algo no es un concepto")"""

            if "rdfs:subPropertyOf" in relation:
                file.write(" ;\n")
                file.write("\t\trdfs:subPropertyOf " + relation["rdfs:subPropertyOf"])

            if "owl:inverseOf" in relation:
                file.write(" ;\n")
                file.write("\t\towl:inverseOf " + relation["owl:inverseOf"])

            if "owl:equivalentProperty" in relation:
                file.write(" ;\n")
                file.write("\t\towl:equivalentProperty " + relation["owl:equivalentProperty"])

            file.write(" ;\n")
            file.write("\t\trdfs:label \"" + relation["label"] + "\"")
            file.write(" .\n\n")

        elif relation["type"] == "owl:FunctionalProperty":
            uri = relation["uri"]
            prefix = relation["prefix"]

            file.write("### " + prefix + ":" + uri + "\n")
            file.write(prefix + ":" + uri + " rdf:type owl:FunctionalProperty")
            file.write(" ;\n")
            file.write("\t\trdfs:label \"" + relation["label"] + "\"")
            file.write(" .\n\n")

    return file, errors


def write_data_properties(file, attribute_blocks, concepts):

    file.write("#################################################################\n"
               "#    Data Properties\n"
               "#################################################################\n\n")

    attributes_reviewed = []

    for id, attribute_block in attribute_blocks.items():

        for attribute in attribute_block["attributes"]:

            uri = attribute["uri"]
            prefix = attribute["prefix"]
            full_name = prefix + ":" + uri
            if full_name in attributes_reviewed:
                continue
            file.write("### " + prefix + ":" + uri + "\n")
            file.write(prefix + ":" + uri + " rdf:type owl:DatatypeProperty")

            if attribute["functional"]:
                file.write(" ,\n")
                file.write("\t\t\towl:FunctionalProperty")
            
            if attribute["domain"]:
                concept_id = attribute["domain"]
                if concept_id in concepts:
                    concept = concepts[concept_id]
                    domain_name = concept["prefix"] + ":" + concept["uri"]
                    file.write(" ;\n")
                    file.write("\t\trdfs:domain " + domain_name)

            if attribute["range"] and attribute["datatype"] and not attribute["hasValue"]:

                if attribute["hasValue"] == False:
                    file.write(" ;\n")
                    file.write("\t\trdfs:range " + attribute["prefix_datatype"] + ":" + attribute["datatype"])
            
            """elif attribute["range"]:
                #Datatype which is declared in a rhombus
                if attribute["hasValue"] == False:
                    file.write(" ;\n")
                    file.write("\t\trdfs:range " + attribute["prefix_datatype"] + ":" + attribute["datatype"])"""

            if "rdfs:subPropertyOf" in attribute:
                file.write(" ;\n")
                file.write("\t\trdfs:subPropertyOf " + attribute["rdfs:subPropertyOf"])

            if "owl:equivalentProperty" in attribute:
                file.write(" ;\n")
                file.write("\t\towl:equivalentProperty " + attribute["owl:equivalentProperty"])

            file.write(" ;\n")
            file.write("\t\trdfs:label \"" + attribute["label"] + "\"")
            file.write(" .\n\n")
            attributes_reviewed.append(full_name)

    return file


def write_concepts(file, concepts, anonymous_concepts, associations, individuals, hexagons, errors, all_relations, anonimous_classes):

    file.write("#################################################################\n"
               "#    Classes\n"
               "#################################################################\n\n")

    for concept_id, association in associations.items():

        concept = association["concept"]
        concept_prefix = concept["prefix"]
        concept_uri = concept["uri"]
        # For now we are not considering unnamed concepts unless they are used for
        # relations of type owl:equivalentClass
        if concept_uri == "":
            continue
        file.write("### " + concept_prefix + ":" + concept_uri + "\n")
        file.write(concept_prefix + ":" + concept_uri + " rdf:type owl:Class ;\n")
        file.write("\trdfs:label \"" + concept["label"] + "\"")

        attribute_blocks = association["attribute_blocks"]
        relations = association["relations"]
        

        for relation_id, relation in relations.items():

            if "type" not in relation:
                continue
            
            # class_descriptor rdfs:subClassOf class_descriptor
            if relation["type"] == "rdfs:subClassOf":
                # class1 subClassOf class2
                if relation["target"] in concepts:
                    target_id = relation["target"]
                    target_name = concepts[target_id]["prefix"] + ":" + concepts[target_id]["uri"]
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf " + target_name)

                #rdfs:subClassOf owl:oneOf (enumerated class)
                elif relation["target"] in hexagons:
                    target_id = relation["target"]
                    complement = hexagons[target_id]
                    file.write(" ; \n")
                    file.write("\trdfs:subClassOf [ rdf:type owl:Class ;")
                    text =  one_of(complement, individuals, errors)
                    file.write(text)
                    file.write("\t\t]")

                #rdfs:subClassOf owl:unionOf or owl:intersectionOf
                elif relation["target"] in anonymous_concepts:
                    complement = anonymous_concepts[relation["target"]]

                    if complement["type"] == "owl:intersectionOf":
                        file.write(" ;")
                        file.write("\trdfs:subClassOf [ rdf:type owl:Class ;")
                        text = intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                    elif complement["type"] == "owl:unionOf":
                        file.write(" ;")
                        file.write("\trdfs:subClassOf [ rdf:type owl:Class ;")
                        text = union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                #rdfs:subClassOf restriction or owl:complementOf
                elif relation["target"] in anonimous_classes:
                    complement = anonimous_classes[relation["target"]]["relations"]
                    if len(complement) > 0:
                        complement = all_relations[complement[0]]
                        if(complement["type"] == "owl:ObjectProperty"):
                            file.write(" ;")
                            file.write("\trdfs:subClassOf ")
                            text = restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)

                        elif(complement["type"] == "owl:complementOf"):
                            file.write(" ;")
                            file.write("\trdfs:subClassOf [ rdf:type owl:Class ;")
                            text = complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)
                            file.write("\t\t]")
                
        for block_id, attribute_block in attribute_blocks.items():
            for attribute in attribute_block["attributes"]:
                if attribute["allValuesFrom"] and attribute["prefix"] and attribute["uri"] and attribute["datatype"]:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n") 
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:allValuesFrom " + attribute["prefix_datatype"] + ":" + attribute["datatype"] + " ]")

                elif attribute["someValuesFrom"] and attribute["prefix"] and attribute["uri"] and attribute["datatype"]:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")    
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:someValuesFrom " + attribute["prefix_datatype"] + ":" + attribute["datatype"] + " ]")

                if attribute["min_cardinality"] is not None and attribute["prefix"] and attribute["uri"]:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:minCardinality \"" + attribute["min_cardinality"] + "\"^^xsd:" +
                                "nonNegativeInteger ]\n")

                if attribute["max_cardinality"] is not None and attribute["prefix"] and attribute["uri"]:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n") 
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:maxCardinality \"" + attribute["max_cardinality"] + "\"^^xsd:" +
                                "nonNegativeInteger ]\n")

                if attribute["cardinality"] is not None and attribute["prefix"] and attribute["uri"]:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")  
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:cardinality \"" + attribute["cardinality"] + "\"^^xsd:" +
                                "nonNegativeInteger ]\n")

                #owl:hasValue
                #the target is a data value
                if attribute["hasValue"] and attribute["prefix"] and attribute["uri"] and attribute["datatype"]:
                    file.write(" ;\n")
                    file.write("\t" + attribute["predicate_restriction"] + " \n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:hasValue " + attribute["prefix_datatype"] + ":" + attribute["datatype"] + " ]")


        for relation_id, relation in relations.items():
            if "type" not in relation:
                continue

            # named_class predicate restriction
            # where restriction can be:
            #   - rdfs:subClassOf (default)
            #   - owl:equivalentClass
            #   - owl:disjointWith
            if relation["type"] == "owl:ObjectProperty":
                text = restrictions(relation, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                # if text is "" that means that the class is not relationate with a restriction
                if text != "":
                    file.write(" ;\n")
                    file.write("\t" + relation["predicate_restriction"] + "\n")
                    file.write(text)
            """if relation["type"] == "owl:ObjectProperty" and (relation["target"] in concepts or \
                relation["target"] in anonymous_concepts or relation["target"] in hexagons or relation["target"] in anonimous_classes):
                
                if relation["allValuesFrom"]:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")
                    text = restrictions(relation, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                    file.write(text)

                elif relation["someValuesFrom"] :
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")
                    text = restrictions(relation, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                    file.write(text)

                if relation["min_cardinality"] is not None:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")  
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    file.write("\t\t  owl:minCardinality \"" + relation["min_cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ]")

                if relation["max_cardinality"] is not None:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    file.write("\t\t  owl:maxCardinality \"" + relation["max_cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ]")

                if relation["cardinality"] is not None:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    file.write("\t\t  owl:cardinality \"" + relation["cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ]")

            # owl:hasValue
            # The target is an individual
            elif relation["type"] == "owl:ObjectProperty" and relation["hasValue"]:
                if relation["target"] in individuals:
                    file.write(" ;\n")
                    file.write("\trdfs:subClassOf \n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    target_id = relation["target"]
                    target_name = individuals[target_id]["prefix"] + ":" + individuals[target_id]["uri"]
                    file.write("\t\t  owl:hasValue " + target_name + " ]")"""

        for relation_id, relation in relations.items():
            if "type" not in relation:
                continue

            if relation["type"] == "owl:disjointWith":
                
                if relation["target"] in concepts:
                    file.write(" ;\n")
                    target_id = relation["target"]
                    target_name = concepts[target_id]["prefix"] + ":" + concepts[target_id]["uri"]
                    file.write("\towl:disjointWith " + target_name)
                
                #owl:disjointWith owl:oneOf
                elif relation["target"] in hexagons:
                    complement = hexagons[relation["target"]]
                    file.write(" ;\n")
                    file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                    text =  one_of(complement, individuals, errors)
                    file.write(text)
                    file.write("\t\t]")

                #owl:disjointWith owl:intersectionOf or owl:unionOf
                elif relation["target"] in anonymous_concepts:
                    complement = anonymous_concepts[relation["target"]]

                    if complement["type"] == "owl:intersectionOf":
                        file.write(" ;\n")
                        file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                        text = intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                    elif complement["type"] == "owl:unionOf":
                        file.write(" ;\n")
                        file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                        text = union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")
                
                #owl:disjointWith restriction or owl:complementOf
                elif relation["target"] in anonimous_classes:
                    complement = anonimous_classes[relation["target"]]["relations"]
                    if len(complement) > 0:
                        complement = all_relations[complement[0]]
                        if(complement["type"] == "owl:ObjectProperty"):
                            file.write(" ;")
                            file.write("\towl:disjointWith ")
                            text = restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)

                        elif(complement["type"] == "owl:complementOf"):
                            file.write(" ;")
                            file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                            text = complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)
                            file.write("\t\t]")

            elif relation["type"] == "owl:complementOf":
                error = {
                        "message": "A class is connected to a owl:complementOf directly. A owl:complementOf can be connected to a class through a class axiom",
                        "shape_id": concept_id,
                        "value": concept_prefix + ":" + concept_uri
                        }
                errors["complementOf"].append(error)
                """file.write(" ;\n")
                text = complement_of(relation, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                file.write(text)"""

            elif relation["type"] == "owl:equivalentClass":
                file.write(" ;\n")
                if relation["target"] in concepts:
                    complement = concepts[relation["target"]]
                    complement_name = complement["prefix"] + ":" + complement["uri"]
                    if complement_name != ":":
                        file.write("\t" + relation["type"] + " " + complement_name)
                    else:
                        file.write("\t" + relation["type"] + " [ rdf:type owl:Restriction ;\n")
                        association = associations[relation["target"]]
                        relation = list(association["relations"].items())[0][1]
                        relation_name = relation["prefix"] + ":" + relation["uri"]
                        target_id = relation["target"]
                        target_name = concepts[target_id]["prefix"] + ":" + concepts[target_id]["uri"]
                        file.write("\towl:onProperty " + relation_name + " ;\n")
                        if relation["someValuesFrom"]:
                            file.write("\towl:someValuesFrom " + target_name + " ]\n")
                        elif relation["allValuesFrom"]:
                            file.write("\towl:allValuesFrom " + target_name + " ]\n")

                # owl:equivalentClass owl:unionOf or owl:intersectionOf
                elif relation["target"] in anonymous_concepts:
                    complement = anonymous_concepts[relation["target"]]

                    if complement["type"] == "owl:intersectionOf":
                        file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                        text = intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                    elif complement["type"] == "owl:unionOf":
                        file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                        text = union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                #owl:equivalentClass owl:oneOf (enumerated class)
                elif relation["target"] in hexagons:
                    complement = hexagons[relation["target"]]
                    file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                    text =  one_of(complement, individuals, errors)
                    file.write(text)
                    file.write("\t\t]")

                #owl:equivalentClass restriction or owl:complementOf
                elif relation["target"] in anonimous_classes:
                    complement = anonimous_classes[relation["target"]]["relations"]
                    if len(complement) > 0:
                        complement = all_relations[complement[0]]
                        if(complement["type"] == "owl:ObjectProperty"):
                            file.write(" ;")
                            file.write("\towl:equivalentClass ")
                            text = restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)

                        elif(complement["type"] == "owl:complementOf"):
                            file.write(" ;")
                            file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                            text = complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)
                            file.write("\t\t]")

            #owl:oneOf (enumerated class)
            elif relation["type"] == "rdf:type" and relation["target"] in hexagons:
                error = {
                        "message": "A class is connected to a owl:oneOf through a rdf:type. A owl:oneOf can be connected to a class through a class axiom",
                        "shape_id": concept_id,
                        "value": concept_prefix + ":" + concept_uri
                        }
                errors["oneOf"].append(error)
                """target_id = relation["target"]
                complement = hexagons[target_id]
                file.write(" ;")
                text =  one_of(complement, individuals, errors)
                file.write(text)"""

            # anonymous class
            elif relation["type"] == "rdf:type" and relation["target"] in anonymous_concepts:
                target_id = relation["target"]
                complement = anonymous_concepts[target_id]
                if complement["type"] == "owl:intersectionOf":
                    error = {
                        "message": "A class is connected to a owl:intersectionOf through a rdf:type. A owl:intersectionOf can be connected to a class through a class axiom",
                        "shape_id": concept_id,
                        "value": concept_prefix + ":" + concept_uri
                        }
                    errors["intersectionOf"].append(error)
                    """file.write(" ;")
                    text = intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                    file.write(text)"""
                elif complement["type"] == "owl:unionOf":
                    error = {
                        "message": "A class is connected to a owl:unionOf through a rdf:type. A owl:unionOf can be connected to a class through a class axiom",
                        "shape_id": concept_id,
                        "value": concept_prefix + ":" + concept_uri
                        }
                    errors["unionOf"].append(error)
                    """file.write(" ;")
                    text = union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                    file.write(text)"""

        for blank_id, blank in anonymous_concepts.items():
            if len(blank["group"]) > 2:
                continue

            if concept_id in blank["group"] and blank["type"] == "owl:disjointWith":
                file.write(" ;\n")
                if blank["group"].index(concept_id) == 0:
                    complement_id = blank["group"][1]
                else:
                    complement_id = blank["group"][0]
                
                if complement_id is None:
                    continue
                
                if complement_id in concepts:
                    complement_concept = concepts[complement_id]
                    complement_name = complement_concept["prefix"] + ":" + complement_concept["uri"]
                    file.write("\t" + blank["type"] + " " + complement_name)

                #owl:disjointWith owl:oneOf
                elif complement_id in hexagons:
                    complement = hexagons[complement_id]
                    file.write("\t" + blank["type"] + " [ rdf:type owl:Class ;")
                    text =  one_of(complement, individuals, errors)
                    file.write(text)
                    file.write("\t\t]")

                #owl:disjointWith owl:intersectionOf or owl:unionOf
                elif complement_id in anonymous_concepts:
                    complement = anonymous_concepts[complement_id]

                    if complement["type"] == "owl:intersectionOf":
                        file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                        text = intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                    elif complement["type"] == "owl:unionOf":
                        file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                        text = union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                #owl:disjointWith restriction or owl:complementOf
                elif complement_id in anonimous_classes:
                    complement = anonimous_classes[complement_id]["relations"]
                    if len(complement) > 0:
                        complement = all_relations[complement[0]]
                        if(complement["type"] == "owl:ObjectProperty"):
                            file.write("\towl:disjointWith ")
                            text = restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)

                        elif(complement["type"] == "owl:complementOf"):
                            file.write("\towl:disjointWith [ rdf:type owl:Class ;")
                            text = complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)
                            file.write("\t\t]")

            elif concept_id in blank["group"] and blank["type"] == "owl:complementOf":
                file.write(" ;\n")
                if blank["group"].index(concept_id) == 0:
                    complement_id = blank["group"][1]
                else:
                    complement_id = blank["group"][0]
                
                if complement_id is None:
                    continue
                
                complement_concept = concepts[complement_id]
                complement_name = complement_concept["prefix"] + ":" + complement_concept["uri"]
                file.write("\t" + blank["type"] + " " + complement_name)

            # namedClass owl:equivalentClass elipse
            elif concept_id in blank["group"] and blank["type"] == "owl:equivalentClass":
                file.write(" ; \n")
                if blank["group"].index(concept_id) == 0:
                    complement_id = blank["group"][1]
                else:
                    complement_id = blank["group"][0]

                if complement_id is None:
                    continue

                if complement_id in concepts:
                    complement = concepts[complement_id]
                    complement_name = complement["prefix"] + ":" + complement["uri"]
                    if complement_name != ":":
                        file.write("\t" + blank["type"] + " " + complement_name)
                    else:
                        file.write("\t" + blank["type"] + " [ rdf:type owl:Restriction ;\n")
                        association = associations[complement_id]
                        relation = list(association["relations"].items())[0][1]
                        relation_name = relation["prefix"] + ":" + relation["uri"]
                        target_id = relation["target"]
                        target_name = concepts[target_id]["prefix"] + ":" + concepts[target_id]["uri"]
                        file.write("\towl:onProperty " + relation_name + " ;\n")
                        if relation["someValuesFrom"]:
                            file.write("\towl:someValuesFrom " + target_name + " ]\n")
                        elif relation["allValuesFrom"]:
                            file.write("\towl:allValuesFrom " + target_name + " ]\n")

                #owl:equivalentClass owl:intersectionOf or owl:unionOf
                elif complement_id in anonymous_concepts:
                    complement = anonymous_concepts[complement_id]

                    if complement["type"] == "owl:intersectionOf":
                        file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                        text = intersection_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")

                    elif complement["type"] == "owl:unionOf":
                        file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                        text = union_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                        file.write(text)
                        file.write("\t\t]")
                
                #owl:equivalentClass owl:oneOf (enumerated class)
                elif complement_id in hexagons:
                    complement = hexagons[complement_id]
                    file.write("\t" + blank["type"] + " [ rdf:type owl:Class ;")
                    text =  one_of(complement, individuals, errors)
                    file.write(text)
                    file.write("\t\t]")

                #owl:equivalentClass restriction or owl:complementOf
                elif complement_id in anonimous_classes:
                    complement = anonimous_classes[complement_id]["relations"]
                    if len(complement) > 0:
                        complement = all_relations[complement[0]]
                        if(complement["type"] == "owl:ObjectProperty"):
                            file.write(" ;")
                            file.write("\towl:equivalentClass ")
                            text = restrictions(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)

                        elif(complement["type"] == "owl:complementOf"):
                            file.write(" ;")
                            file.write("\towl:equivalentClass [ rdf:type owl:Class ;")
                            text = complement_of(complement, concepts, errors, hexagons, anonymous_concepts, individuals, all_relations, anonimous_classes)
                            file.write(text)
                            file.write("\t\t]")

        file.write(" .\n\n")

    return file


def write_instances(file, individuals):

    file.write("#################################################################\n"
               "#    Instances\n"
               "#################################################################\n\n")

    for ind_id, individual in individuals.items():

        prefix = individual["prefix"]
        uri = individual["uri"]
        types = individual["type"]
        file.write("### " + prefix + ":" + uri + "\n")
        file.write(prefix + ":" + uri + " rdf:type owl:NamedIndividual")
        if types is None:
            file.write(" .\n")
        else:
            for type in types:
                file.write(";\n\t\trdf:type " + type)

        file.write(" .\n\n")

    return file


def write_general_axioms(file, concepts, anonymous_concepts, individuals, hexagons):

    file.write("#################################################################\n"
               "#    General Axioms\n"
               "#################################################################\n\n")

    for blank_id, blank in anonymous_concepts.items():
        if len(blank["group"]) > 2 and blank["type"] in ["owl:disjointWith"]:
            file.write("[ rdf:type owl:AllDisjointClasses ;\n")
            file.write("  owl:members ( \n")

            concept_names = [concepts[id]["prefix"] + ":" + concepts[id]["uri"] for id in blank["group"]]
            for name in concept_names:
                file.write("\t\t" + name + "\n")
            file.write("\t\t)")
            file.write("] .")

    for hex_id, hexagon in hexagons.items():

        if len(hexagon["group"]) > 2 and hexagon["type"] in ["owl:AllDifferent"]:
            file.write("[ rdf:type owl:AllDifferent ;\n")
            file.write("  owl:distinctMembers ( \n")

            individual_names = [individuals[id]["prefix"] + ":" + individuals[id]["uri"] for id in hexagon["group"]]

            for name in individual_names:
                file.write("\t\t" + name + "\n")
            file.write("\t\t)")
            file.write("] .")

    return file

def write_triplets(file, individuals, associations, values):

    for id, association in associations.items():
        subject = association["individual"]["prefix"] + ":" + association["individual"]["uri"]
        types = association["individual"]["type"]
        relations = association["relations"]
        attributes = association["attributes"]

        for relation_id, relation in relations.items():
            predicate = relation["prefix"] + ":" + relation["uri"]
            target_id = relation["target"]
            object = individuals[target_id]["prefix"] + ":" + individuals[target_id]["uri"]
            file.write(subject + " " + predicate + " " + object + " .\n")

        for attribute_id, attribute in attributes.items():
            predicate = attribute["prefix"] + ":" + attribute["uri"]
            target_id = attribute["target"]
            if values[target_id]["type"] is not None:
                object = "\"" + values[target_id]["value"] + "\"" + "^^" + values[target_id]["type"]
            
            elif values[target_id]["lang"] is not None:
                object = "\"" + values[target_id]["value"] + "\"" + "@" + values[target_id]["lang"]
            else:
                object = "\"" + values[target_id]["value"] + "\""
            file.write(subject + " " + predicate + " " + object + " .\n")

    return file
    