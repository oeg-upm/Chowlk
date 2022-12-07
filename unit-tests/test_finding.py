
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_ontologies():

    tests_path = os.path.dirname(os.path.abspath(__file__))
    inputs_path = os.path.join(tests_path, "inputs")
    outputs_path = os.path.join(tests_path, "outputs")
    converter_path = os.path.join(tests_path, "..\converter.py")

    for filename in os.listdir(inputs_path):
        input_filepath = os.path.join(inputs_path, filename)
        output_filepath = os.path.join(outputs_path, filename[:-3] + "ttl")
        log_filepath = os.path.join(outputs_path, filename[:-4] + "_log.txt")
        print("\nGenerating ontology (output) " + filename + "\n")
        command = r'python ' + converter_path + ' ' + input_filepath + \
            ' ' + output_filepath + r' --type ontology --format ttl > ' + \
            log_filepath
        os.system(command)


def test():
    all_test_passed = True
    tests_path = os.path.dirname(os.path.abspath(__file__))
    desired_outputs_path = os.path.join(tests_path, "desired_outputs")
    outputs_path = os.path.join(tests_path, "outputs")
    outputs_tests = os.listdir(outputs_path)

    for filename in os.listdir(desired_outputs_path):
        if filename in outputs_tests:
            # A test is performed per ontology and log generated (both in the same test)
            if filename[-4:] == ".ttl":
                print("Performing test " + filename + ". Result: ")
                output_filepath = os.path.join(outputs_path, filename)
                desired_output_filepath = os.path.join(
                    desired_outputs_path, filename)
                if compare_ontologies(output_filepath, desired_output_filepath):
                    output_log_filepath = os.path.join(outputs_path, filename[:-4] + "_log.txt")
                    desired_output_log_filepath = os.path.join(desired_outputs_path, filename[:-4] + "_log.txt")
                    if compare_logs(output_log_filepath, desired_output_log_filepath):
                        print("Test passed\n")
                    else:
                        all_test_passed = False
                        print("Test failed. Logs are not equal\n")
                else:
                    all_test_passed = False
        else:
            print("Output " + filename +
                  " file has not been generated correctly.\n")
            all_test_passed = False
    return all_test_passed


def compare_ontologies(o1, o2):
    # We want to compare two fields in order to find
    # the first line where they are not equals
    file1 = open(o1, 'r')
    linesFile1 = file1.readlines()
    file2 = open(o2, 'r')
    linesFile2 = file2.readlines()
    equals = True
    # The files can have different length
    # For that reason it is neccesary to find the minimun length
    minimun_length = len(linesFile1)
    if minimun_length > len(linesFile2):
        minimun_length = len(linesFile2)

    for i in range(minimun_length):
        if linesFile1[i] != linesFile2[i]:
            print("Test failed. Files are not equal in line " + str(i+1) + "\n")
            equals = False
            break

    # If they have different lengths and until minimum_length
    # are equal, it is neccesary to indicate that one is greater
    # than the other
    if equals and len(linesFile1) != len(linesFile2):
        print("Test failed. One file is greater than the other. The minimun lenght is " +
              str(i+1) + ". Until that line they are equals\n")
        equals = False 

    file1.close()
    file2.close()
    return equals

def compare_logs(l1, l2):
    file1 = open(l1, 'r')
    file2 = open(l2, 'r')
    passed = file1.read() == file2.read()
    file1.close()
    file2.close()
    return passed

#Funtion to remove all the files in the repository output
def empty_repository():
    tests_path = os.path.dirname(os.path.abspath(__file__))
    outputs_path = os.path.join(tests_path, "outputs")
    for f in os.listdir(outputs_path):
        os.remove(os.path.join(outputs_path, f))
    return

if __name__ == "__main__":
    empty_repository()
    generate_ontologies()
    if test():
        print("\n All tests passed")
"""
class TestFindingFunctions(unittest.TestCase):

    def test_concepts(self):

        test = read_drawio_xml("tests/inputs_finding/test_concepts.xml")
        finder = Finder(test)
        concepts, _ = finder.find_concepts_and_attributes()
        for id, concept in concepts.items():
            self.assertEqual(id, "2")
            self.assertEqual(concept["prefix"], "ns")
            self.assertEqual(concept["uri"], "Class")

    def test_unnamed(self):

        test = read_drawio_xml("tests/inputs_finding/test_unnamed.xml")
        finder = Finder(test)
        concepts, _ = finder.find_concepts_and_attributes()
        for id, concept in concepts.items():
            self.assertEqual(concept["prefix"], "")
            self.assertEqual(concept["uri"], "")

    def test_namespaces(self):

        test = read_drawio_xml("tests/inputs_finding/test_namespaces.xml")
        finder = Finder(test)
        namespaces = finder.find_namespaces()
        for prefix, uri in namespaces.items():
            self.assertEqual(prefix in ["base", "saref"], True)
            self.assertEqual(uri in ["http://theOntology.namespace.com", "http://saref.com"], True)

    def test_intersection_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_intersection_1.xml")
        finder = Finder(test)
        finder.find_relations()
        ellipses = finder.find_ellipses()
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:intersectionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_intersection_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_intersection_2.xml")
        finder = Finder(test)
        finder.find_relations()
        ellipses = finder.find_ellipses()
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:intersectionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_union_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_union_1.xml")
        finder = Finder(test)
        finder.find_relations()
        ellipses = finder.find_ellipses()
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:unionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_union_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_union_2.xml")
        finder = Finder(test)
        finder.find_relations()
        ellipses = finder.find_ellipses()
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:unionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_equivalent_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_equivalent_1.xml")
        finder = Finder(test)
        finder.find_relations()
        ellipses = finder.find_ellipses()
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:equivalentClass")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_disjoint_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_disjoint_1.xml")
        finder = Finder(test)
        finder.find_relations()
        ellipses = finder.find_ellipses()
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:disjointWith")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_individual_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_individual_1.xml")
        finder = Finder(test)
        individuals = finder.find_individuals()
        for id, individual in individuals.items():
            self.assertEqual(individual["prefix"], "ns")
            self.assertEqual(individual["uri"], "Individual1")
            self.assertEqual(individual["type"] is None, True)

    def test_individual_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_individual_2.xml")
        finder = Finder(test)
        individuals = finder.find_individuals()
        for id, individual in individuals.items():
            self.assertEqual(individual["prefix"], "ns")
            self.assertEqual(individual["uri"], "Individual1")
            self.assertEqual(individual["type"] is None, True)

    def test_relations_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_1.xml")
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "rdfs:subClassOf")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_relations_8(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_8.xml")
        finder = Finder(test)
        relations = finder.find_relations()
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "rdfs:subClassOf")
            self.assertEqual(relation["source"], "4")
            self.assertEqual(relation["target"], "3")

    def test_relations_9(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_9.xml")
        finder = Finder(test)
        relations = finder.find_relations()
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "owl:equivalentClass")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_relations_10(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_10.xml")
        finder = Finder(test)
        relations = finder.find_relations()
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "owl:equivalentClass")
            self.assertEqual(relation["source"], "3")
            self.assertEqual(relation["target"], "2")

    def test_relations_11(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_11.xml")
        finder = Finder(test)
        relations = finder.find_relations()
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "owl:disjointWith")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_relations_12(self):

        test = read_drawio_xml("tests/inputs_finding/test_relation_12.xml")
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
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
        finder = Finder(test)
        relations = finder.find_relations()
        for id, relation in relations.items():
            self.assertEqual(relation["type"], "rdf:type")
            self.assertEqual(relation["source"], "5")
            self.assertEqual(relation["target"], "4")

    def test_attributes_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_attributes_1.xml")
        finder = Finder(test)
        _, attribute_blocks = finder.find_concepts_and_attributes()
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
        finder = Finder(test)
        _, attribute_blocks = finder.find_concepts_and_attributes()
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
        finder = Finder(test)
        _, attribute_blocks = finder.find_concepts_and_attributes()
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
        finder = Finder(test)
        _, attribute_blocks = finder.find_concepts_and_attributes()
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
        finder = Finder(test)
        _, attribute_blocks = finder.find_concepts_and_attributes()
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
        finder = Finder(test)
        _, attribute_blocks = finder.find_concepts_and_attributes()
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

    def test_rhombus_1(self):

        test = read_drawio_xml("tests/inputs_finding/test_rhombus_1.xml")
        finder = Finder(test)
        rhombuses = finder.find_rhombuses()
        for id, rhombus in rhombuses.items():
            self.assertEqual(id, "2")
            self.assertEqual(rhombus["type"], "owl:ObjectProperty")
            self.assertEqual(rhombus["prefix"], "ns")
            self.assertEqual(rhombus["uri"], "objectProperty1")

    def test_rhombus_2(self):

        test = read_drawio_xml("tests/inputs_finding/test_rhombus_2.xml")
        finder = Finder(test)
        rhombuses = finder.find_rhombuses()
        for id, rhombus in rhombuses.items():
            self.assertEqual(id, "2")
            self.assertEqual(rhombus["type"], "owl:DatatypeProperty")
            self.assertEqual(rhombus["prefix"], "ns")
            self.assertEqual(rhombus["uri"], "objectProperty1")

if __name__ == "__main__":
    unittest.main()

"""
