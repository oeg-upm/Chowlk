import xml.etree.ElementTree as ET
import argparse
from finding import *
from geometry import get_corners
from associations import resolve_concept_reference, concept_relations_association
from associations import concept_attributes_association, individuals_type_identification
from associations import individuals_type_identification_rdf, individuals_associations_rdf
from writer import get_ttl_template, write_ontology_metadata

"""
# This lines are for compresed XML files
compressed_xml = root[0].text
coded_xml = base64.b64decode(compressed_xml)
xml_string = unquote(zlib.decompress(coded_xml, -15).decode('utf8'))
mxGraphModel = ET.fromstring(xml_string)
"""


def transform_ontology(root, filename):
    all_elements = find_elements(root)
    concepts, attribute_blocks, relations = all_elements[0:3]
    individuals, anonymous_concepts, ontology_metadata, namespaces = all_elements[3:]
    attribute_blocks = resolve_concept_reference(attribute_blocks, concepts)

    associations = concept_attributes_association(concepts, attribute_blocks)
    associations, relations = concept_relations_association(associations, relations)
    type_relations = [relation for relation in relations if relation["type"] == "rdf:type"]
    individuals_associations = individuals_type_identification(individuals, associations, type_relations)

    file, onto_prefix, onto_uri = get_ttl_template(filename, namespaces)
    file = write_ontology_metadata(file, ontology_metadata, onto_uri)

    file.write("#################################################################\n"
               "#    Object Properties\n"
               "#################################################################\n\n")

    for relation in relations:

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
                domain_name = [concept["prefix"] + ":" + concept["uri"]
                               for concept in concepts if concept["id"] == relation["source"]][0]
                if domain_name != ":":
                    file.write(" ;\n")
                    file.write("\t\trdfs:domain " + domain_name)

            if relation["range"]:
                file.write(" ;\n")
                try:
                    range_name = [concept["prefix"] + ":" + concept["uri"]
                                  for concept in concepts if concept["id"] == relation["target"]][0]

                    file.write("\t\trdfs:range " + range_name)
                except:
                    group_node = [blank for blank in anonymous_concepts if blank["id"] == relation["target"]][0]
                    concept_ids = group_node["group"]
                    concept_names = [concept["prefix"] + ":" + concept["uri"] for concept in concepts
                                     if concept["id"] in concept_ids]
                    file.write("\t\trdfs:range [ " + group_node["type"] + " ( \n")
                    for name in concept_names:
                        file.write("\t\t\t\t\t\t" + name + "\n")

                    file.write("\t\t\t\t\t) ;\n")
                    file.write("\t\t\t\t\trdf:type owl:Class\n")
                    file.write("\t\t\t\t\t]")


            file.write(" .\n\n")


    file.write("#################################################################\n"
               "#    Data Properties\n"
               "#################################################################\n\n")

    attributes_reviewed = []
    for attribute_block in attribute_blocks:

        source_id = attribute_block["concept_associated"]

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
                domain_name = [concept["prefix"] + ":" + concept["uri"]
                               for concept in concepts if concept["id"] == source_id][0]
                file.write(" ;\n")
                file.write("\t\trdfs:domain " + domain_name)

            if attribute["range"]:
                file.write(" ;\n")
                file.write("\t\trdfs:range xsd:" + attribute["datatype"].lower())

            file.write(" .\n\n")
            attributes_reviewed.append(full_name)



    file.write("#################################################################\n"
               "#    Classes\n"
               "#################################################################\n\n")

    for association in associations:

        concept = association["concept"]
        concept_prefix = concept["prefix"]
        concept_uri = concept["uri"]
        # For now we are not considering unnamed concepts unless they are used for
        # relations of type owl:equivalentClass
        if concept_uri == "":
            continue
        file.write("### " + concept_prefix + ":" + concept_uri + "\n")
        file.write(concept_prefix + ":" + concept_uri + " rdf:type owl:Class")

        attribute_blocks = association["attribute_blocks"]
        relations = association["relations"]
        subclassof_statement_done = False
        for relation in relations:
            if relation["type"] == "rdfs:subClassOf":
                file.write(" ;\n")
                file.write("\trdfs:subClassOf " + relation["target_name"])
                subclassof_statement_done = True

        for attribute_block in attribute_blocks:
            for attribute in attribute_block["attributes"]:
                if attribute["allValuesFrom"]:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:allValuesFrom xsd:" + attribute["datatype"] + " ]")

                elif attribute["someValuesFrom"]:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:someValuesFrom xsd:" + attribute["datatype"] + " ]")

                if attribute["min_cardinality"] is not None:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:minQualifiedCardinality \"" + attribute["min_cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ;\n")
                    file.write("\t\t  owl:onDataRange xsd:" + attribute["datatype"] + " ]")

                if attribute["max_cardinality"] is not None:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + attribute["prefix"] + ":" + attribute["uri"] + " ;\n")
                    file.write("\t\t  owl:maxQualifiedCardinality \"" + attribute["max_cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ;\n")
                    file.write("\t\t  owl:onDataRange xsd:" + attribute["datatype"] + " ]")

        for relation in relations:
            if relation["type"] == "owl:ObjectProperty":
                if relation["allValuesFrom"]:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    # Target name only applies when the target is a class
                    if "target_name" in relation:
                        file.write("\t\t  owl:allValuesFrom " + relation["target_name"] + " ]")
                    # Otherwise the target is an blank node of type intersection, union, etc.
                    else:
                        group_node = [blank for blank in anonymous_concepts if blank["id"] == relation["target"]][0]
                        concept_ids = group_node["group"]
                        concept_names = [concept["prefix"] + ":" + concept["uri"] for concept in concepts
                                         if concept["id"] in concept_ids]
                        file.write("\t\t  owl:allValuesFrom [ " + group_node["type"] + " ( \n")
                        for name in concept_names:
                            file.write("\t\t\t\t\t\t" + name + "\n")

                        file.write("\t\t\t\t\t) ;\n")
                        file.write("\t\t\t\t\trdf:type owl:Class\n")
                        file.write("\t\t\t\t\t] ]")


                elif relation["someValuesFrom"]:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    # Target name only applies when the target is a class
                    if "target_name" in relation:
                        file.write("\t\t  owl:someValuesFrom " + relation["target_name"] + " ]")
                    # Otherwise the target is an blank node of type intersection, union, etc.
                    else:
                        group_node = [blank for blank in anonymous_concepts if blank["id"] == relation["target"]][0]
                        concept_ids = group_node["group"]
                        concept_names = [concept["prefix"] + ":" + concept["uri"] for concept in concepts
                                         if concept["id"] in concept_ids]
                        file.write("\t\t  owl:someValuesFrom [ " + group_node["type"] + " ( \n")
                        for name in concept_names:
                            file.write("\t\t\t\t\t\t" + name + "\n")

                        file.write("\t\t\t\t\t) ;\n")
                        file.write("\t\t\t\t\trdf:type owl:Class\n")
                        file.write("\t\t\t\t\t] ]")

                if relation["min_cardinality"] is not None:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    file.write("\t\t  owl:minQualifiedCardinality \"" + relation["min_cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ;\n")
                    file.write("\t\t  owl:onClass " + relation["target_name"] + " ]")

                if relation["max_cardinality"] is not None:
                    if not subclassof_statement_done:
                        file.write(" ;\n")
                        file.write("\trdfs:subClassOf \n")
                        subclassof_statement_done = True
                    else:
                        file.write(" ,\n")
                    file.write("\t\t[ rdf:type owl:Restriction ;\n")
                    file.write("\t\t  owl:onProperty " + relation["prefix"] + ":" + relation["uri"] + " ;\n")
                    file.write("\t\t  owl:maxQualifiedCardinality \"" + relation["max_cardinality"] + "\"^^xsd:" +
                               "nonNegativeInteger ;\n")
                    file.write("\t\t  owl:onClass " + relation["target_name"] + " ]")

        for relation in relations:
            if relation["type"] == "owl:disjointWith":
                file.write(" ;\n")
                file.write("\towl:disjointWith " + relation["target_name"])

            elif relation["type"] == "owl:equivalentClass":
                file.write(" ;\n")
                complement_concept = [concept for concept in concepts if relation["target"] == concept["id"]]
                complement_gate = [gate for gate in anonymous_concepts if relation["target"] == gate["id"]]

                if len(complement_concept) > 0:
                    complement = complement_concept[0]
                    complement_name = complement["prefix"] + ":" + complement["uri"]
                    if complement_name != ":":
                        file.write("\t" + relation["type"] + " " + complement_name)
                    else:
                        file.write("\t" + relation["type"] + " [ rdf:type owl:Restriction ;\n")
                        unnamed_id = complement["id"]
                        association = [association for association in associations
                                        if association["concept"]["id"] == unnamed_id][0]
                        relation = association["relations"][0]
                        relation_name = relation["prefix"] + ":" + relation["uri"]
                        target_name = relation["target_name"]
                        file.write("\towl:onProperty " + relation_name + " ;\n")
                        if relation["someValuesFrom"]:
                            file.write("\towl:someValuesFrom " + target_name + " ]\n")
                        elif relation["allValuesFrom"]:
                            file.write("\towl:allValuesFrom " + target_name + " ]\n")
                elif len(complement_gate) > 0:
                    complement = complement_gate[0]
                    ids = complement["group"]
                    file.write("\t" + relation["type"] + " [ " + complement["type"] + " ( \n")
                    for id in ids:
                        concept_involved = [concept["prefix"] + ":" + concept["uri"]
                                            for concept in concepts if concept["id"] == id][0]
                        file.write("\t\t\t\t" + concept_involved + "\n")
                    file.write("\t\t\t\t)")
                    file.write("\t\t]")

        for blank in anonymous_concepts:

            if len(blank["group"]) > 2:
                continue

            if concept["id"] in blank["group"] and blank["type"] == "owl:disjointWith":
                file.write(" ;\n")
                if blank["group"].index(concept["id"]) == 0:
                    complement_id = blank["group"][1]
                else:
                    complement_id = blank["group"][0]
                complement_concept = [concept for concept in concepts if concept["id"] == complement_id][0]
                complement_name = complement_concept["prefix"] + ":" + complement_concept["uri"]
                file.write("\t" + blank["type"] + " " + complement_name)

            elif concept["id"] in blank["group"] and blank["type"] == "owl:equivalentClass":
                file.write(" ; \n")
                if blank["group"].index(concept["id"]) == 0:
                    complement_id = blank["group"][1]
                else:
                    complement_id = blank["group"][0]

                complement_concept = [concept for concept in concepts if concept["id"] == complement_id]
                complement_gate = [gate for gate in anonymous_concepts if gate["id"] == complement_id]

                if len(complement_concept) > 0:
                    complement = complement_concept[0]
                    complement_name = complement["prefix"] + ":" + complement["uri"]
                    if complement_name != ":":
                        file.write("\t" + blank["type"] + " " + complement_name)
                    else:
                        file.write("\t" + blank["type"] + " [ rdf:type owl:Restriction ;\n")
                        unnamed_id = complement["id"]
                        association = [association for association in associations
                                       if association["concept"]["id"] == unnamed_id][0]
                        relation = association["relations"][0]
                        relation_name = relation["prefix"] + ":" + relation["uri"]
                        target_name = relation["target_name"]
                        file.write("\towl:onProperty " + relation_name + " ;\n")
                        if relation["someValuesFrom"]:
                            file.write("\towl:someValuesFrom " + target_name + " ]\n")
                        elif relation["allValuesFrom"]:
                            file.write("\towl:allValuesFrom " + target_name + " ]\n")
                elif len(complement_gate) > 0:
                    complement = complement_gate[0]
                    ids = complement["group"]
                    file.write("\t" + blank["type"] + " [ " + complement["type"] + " ( \n")
                    for id in ids:
                        concept_involved = [concept["prefix"] + ":" + concept["uri"]
                                            for concept in concepts if concept["id"] == id][0]
                        file.write("\t\t\t\t" + concept_involved + "\n")
                    file.write("\t\t\t\t)")
                    file.write("\t\t]")



        file.write(" .\n\n")

    file.write("#################################################################\n"
               "#    Instances\n"
               "#################################################################\n\n")

    for individual in individuals_associations:

        prefix = individual["individual"]["prefix"]
        uri = individual["individual"]["uri"]
        type = individual["individual"]["type"]
        file.write("### " + prefix + ":" + uri + "\n")
        file.write(prefix + ":" + uri + " rdf:type owl:NamedIndividual ,\n")
        file.write("\t\t" + type + " .\n\n")

    file.write("#################################################################\n"
               "#    General Axioms\n"
               "#################################################################\n\n")

    for blank in anonymous_concepts:
        if len(blank["group"]) > 2 and blank["type"] in ["owl:disjointWith"]:
            file.write("[ rdf:type owl:AllDisjointClasses ;\n")
            file.write("  owl:members ( \n")
            concept_names = [concept["prefix"] + ":" + concept["uri"]
                             for concept in concepts if concept["id"] in blank["group"]]
            for name in concept_names:
                file.write("\t\t" + name + "\n")
            file.write("\t\t)")
            file.write("] .")

def transform_rdf(root, filename):

    individuals = find_individuals(root)
    relations = find_relations(root)
    namespaces = find_namespaces(root)
    #metadata = find_metadata(root)
    concepts, attributes = find_concepts_and_attributes(root)

    individuals = individuals_type_identification_rdf(individuals, concepts, relations)
    associations = individuals_associations_rdf(individuals, relations)

    file, onto_prefix, onto_uri = get_ttl_template(filename, namespaces)
    #file = write_ontology_metadata(file, metadata, onto_uri)

    for association in associations:

        subject = association["individual"]["prefix"] + ":" + association["individual"]["uri"]
        concept = association["individual"]["type"]
        relations = association["relations"]

        file.write(subject + " rdf:type " + concept)

        for relation in relations:
            file.write(" ;\n")
            predicate = relation["prefix"] + ":" + relation["uri"]
            object = relation["target_name"]

            file.write("\t" + predicate + " " + object)

        file.write(" .\n\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("diagram_path")
    parser.add_argument("output_path")
    parser.add_argument("type")
    args = parser.parse_args()

    tree = ET.parse(args.diagram_path)
    mxfile = tree.getroot()
    root = mxfile[0][0][0]

    # Eliminate children related to the whole white template
    for elem in root:
        if elem.attrib["id"] == "0":
            root.remove(elem)
            break
    for elem in root:
        if elem.attrib["id"] == "1":
            root.remove(elem)
            break

    if args.type == "ontology":
        transform_ontology(root, args.output_path)
    elif args.type == "rdf":
        transform_rdf(root, args.output_path)
    else:
        raise ValueError("Not a correct option of data")