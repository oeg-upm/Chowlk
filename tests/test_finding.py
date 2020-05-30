import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from modules.finding import *
from modules.utils import read_drawio_xml

class TestFindingFunctions(unittest.TestCase):

    def test_concepts(self):

        test = read_drawio_xml("tests/inputs_finding/test_concepts.xml")
        concepts, _ = find_concepts_and_attributes(test)
        for id, concept in concepts.items():
            self.assertEqual(id, "2")
            self.assertEqual(concept["prefix"], "ns")
            self.assertEqual(concept["uri"], "Class")

    def test_unnamed(self):

        test = read_drawio_xml("tests/inputs_finding/test_unnamed.xml")
        concepts, _ = find_concepts_and_attributes(test)
        for id, concept in concepts.items():
            self.assertEqual(concept["prefix"], "")
            self.assertEqual(concept["uri"], "")

    def test_namespaces(self):

        test = read_drawio_xml("tests/inputs_finding/test_namespaces.xml")
        namespaces = find_namespaces(test)
        for prefix, uri in namespaces.items():
            self.assertEqual(prefix in ["base", "saref"], True)
            self.assertEqual(uri in ["http://theOntology.namespace.com", "http://saref.com"], True)

    def test_intersection_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_intersection_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:intersectionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_intersection_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_intersection_2.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:intersectionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_union_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_union_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:unionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_union_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_union_2.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:unionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_equivalent_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_equivalent_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:equivalentClass")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_disjoint_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_disjoint_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:disjointWith")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_individual_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_individual_1.xml")
        individuals = find_individuals(test)
        for id, individual in individuals.items():
            self.assertEqual(individual["prefix"], "ns")
            self.assertEqual(individual["uri"], "Individual1")
            self.assertEqual(individual["type"] is None, True)

    def test_individual_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_individual_2.xml")
        individuals = find_individuals(test)
        for id, individual in individuals.items():
            self.assertEqual(individual["prefix"], "ns")
            self.assertEqual(individual["uri"], "Individual1")
            self.assertEqual(individual["type"] is None, True)

    def test_relations_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_1.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "2")
            self.assertEqual(relation["target"], "3")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["allValuesFrom"], True)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_2.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "2")
            self.assertEqual(relation["target"], "3")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["allValuesFrom"], True)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_3(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_3.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "2")
            self.assertEqual(relation["target"], "3")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["allValuesFrom"], True)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_4(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_4.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "2")
            self.assertEqual(relation["target"], "3")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["someValuesFrom"], True)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_5(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_5.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "2")
            self.assertEqual(relation["target"], "3")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["someValuesFrom"], True)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_6(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_6.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "2")
            self.assertEqual(relation["target"], "3")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["someValuesFrom"], True)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_7(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_7.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "rdfs:subClassOf")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_relations_8(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_8.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "rdfs:subClassOf")
            self.assertEqual(relation["source"], "4")
            self.assertEqual(relation["target"], "3")

    def test_relations_9(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_9.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "owl:equivalentClass")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_relations_10(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_10.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "owl:equivalentClass")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")

    def test_relations_11(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_11.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "owl:disjointWith")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_relations_12(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_12.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")
            self.assertEqual(relation["domain"], False)
            self.assertEqual(relation["range"], False)
            self.assertEqual(relation["someValuesFrom"], False)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_13(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_13.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")
            self.assertEqual(relation["domain"], False)
            self.assertEqual(relation["range"], False)
            self.assertEqual(relation["someValuesFrom"], False)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_14(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_14.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["someValuesFrom"], False)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_15(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_15.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["someValuesFrom"], False)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)


    def test_relations_16(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_16.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")
            self.assertEqual(relation["domain"], True)
            self.assertEqual(relation["range"], False)
            self.assertEqual(relation["someValuesFrom"], False)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_17(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_17.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["prefix"], "ns")
            self.assertEqual(relation["uri"], "objectProperty")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")
            self.assertEqual(relation["domain"], False)
            self.assertEqual(relation["range"], True)
            self.assertEqual(relation["someValuesFrom"], False)
            self.assertEqual(relation["functional"], False)
            self.assertEqual(relation["inverse_functional"], False)
            self.assertEqual(relation["transitive"], False)
            self.assertEqual(relation["symmetric"], False)

    def test_relations_18(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_18.xml")
        relations = find_relations(test)
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "rdf:type")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_attributes_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_1.xml")
        _, attribute_blocks = find_concepts_and_attributes(test)
        for id, attribute_block in attribute_blocks.items():
            self.assertEqual(attribute_block["concept_associated"], "3")
            attributes = attribute_block["attributes"]
            for attribute in attributes:
                self.assertEqual(attribute["prefix"] in ["ns"], True)
                self.assertEqual(attribute["uri"] in ["datatypeProperty1"], True)
                self.assertEqual(attribute["datatype"] is None, True)
                self.assertEqual(attribute["domain"], False)
                self.assertEqual(attribute["range"], False)
                self.assertEqual(attribute["allValuesFrom"], False)
                self.assertEqual(attribute["someValuesFrom"], False)
                self.assertEqual(attribute["functional"], False)
                self.assertEqual(attribute["min_cardinality"] is None, True)
                self.assertEqual(attribute["max_cardinality"] is None, True)

    def test_attributes_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_2.xml")
        _, attribute_blocks = find_concepts_and_attributes(test)
        for id, attribute_block in attribute_blocks.items():
            self.assertEqual(attribute_block["concept_associated"], "3")
            attributes = attribute_block["attributes"]
            for attribute in attributes:
                self.assertEqual(attribute["prefix"] in ["ns"], True)
                self.assertEqual(attribute["uri"] in ["datatypeProperty1"], True)
                self.assertEqual(attribute["datatype"] in ["datatype"], True)
                self.assertEqual(attribute["domain"], True)
                self.assertEqual(attribute["range"], True)
                self.assertEqual(attribute["allValuesFrom"], False)
                self.assertEqual(attribute["someValuesFrom"], False)
                self.assertEqual(attribute["functional"], False)
                self.assertEqual(attribute["min_cardinality"] is None, True)
                self.assertEqual(attribute["max_cardinality"] is None, True)

    def test_attributes_3(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_3.xml")
        _, attribute_blocks = find_concepts_and_attributes(test)
        for id, attribute_block in attribute_blocks.items():
            self.assertEqual(attribute_block["concept_associated"], "3")
            attributes = attribute_block["attributes"]
            for attribute in attributes:
                self.assertEqual(attribute["prefix"] in ["ns"], True)
                self.assertEqual(attribute["uri"] in ["datatypeProperty1"], True)
                self.assertEqual(attribute["datatype"] is None, True)
                self.assertEqual(attribute["domain"], True)
                self.assertEqual(attribute["range"], False)
                self.assertEqual(attribute["allValuesFrom"], False)
                self.assertEqual(attribute["someValuesFrom"], False)
                self.assertEqual(attribute["functional"], False)
                self.assertEqual(attribute["min_cardinality"] is None, True)
                self.assertEqual(attribute["max_cardinality"] is None, True)

    def test_attributes_4(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_4.xml")
        _, attribute_blocks = find_concepts_and_attributes(test)
        for id, attribute_block in attribute_blocks.items():
            self.assertEqual(attribute_block["concept_associated"], "3")
            attributes = attribute_block["attributes"]
            for attribute in attributes:
                self.assertEqual(attribute["prefix"] in ["ns"], True)
                self.assertEqual(attribute["uri"] in ["datatypeProperty1"], True)
                self.assertEqual(attribute["datatype"] in ["datatype"], True)
                self.assertEqual(attribute["domain"], False)
                self.assertEqual(attribute["range"], True)
                self.assertEqual(attribute["allValuesFrom"], False)
                self.assertEqual(attribute["someValuesFrom"], False)
                self.assertEqual(attribute["functional"], False)
                self.assertEqual(attribute["min_cardinality"] is None, True)
                self.assertEqual(attribute["max_cardinality"] is None, True)

    def test_attributes_5(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_5.xml")
        _, attribute_blocks = find_concepts_and_attributes(test)
        for id, attribute_block in attribute_blocks.items():
            self.assertEqual(attribute_block["concept_associated"], "3")
            attributes = attribute_block["attributes"]
            for attribute in attributes:
                self.assertEqual(attribute["prefix"] in ["ns"], True)
                self.assertEqual(attribute["uri"] in ["datatypeProperty1"], True)
                self.assertEqual(attribute["datatype"] is None, True)
                self.assertEqual(attribute["domain"], True)
                self.assertEqual(attribute["range"], False)
                self.assertEqual(attribute["allValuesFrom"], False)
                self.assertEqual(attribute["someValuesFrom"], False)
                self.assertEqual(attribute["functional"], True)
                self.assertEqual(attribute["min_cardinality"] is None, True)
                self.assertEqual(attribute["max_cardinality"] is None, True)

    def test_attributes_6(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_6.xml")
        _, attribute_blocks = find_concepts_and_attributes(test)
        for id, attribute_block in attribute_blocks.items():
            self.assertEqual(attribute_block["concept_associated"], "3")
            attributes = attribute_block["attributes"]
            for attribute in attributes:
                self.assertEqual(attribute["prefix"] in ["ns"], True)
                self.assertEqual(attribute["uri"] in ["datatypeProperty1"], True)
                self.assertEqual(attribute["datatype"] in ["datatype"], True)
                self.assertEqual(attribute["domain"], True)
                self.assertEqual(attribute["range"], True)
                self.assertEqual(attribute["allValuesFrom"], False)
                self.assertEqual(attribute["someValuesFrom"], False)
                self.assertEqual(attribute["functional"], False)
                self.assertEqual(attribute["min_cardinality"], "1")
                self.assertEqual(attribute["max_cardinality"] is None, True)

if __name__ == "__main__":
    unittest.main()