import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from modules.finding import *
from modules.utils import read_drawio_xml

class TestFindingFunctions(unittest.TestCase):

    def test_concepts(self):

        test = read_drawio_xml("tests/inputs/test_concepts.xml")
        concepts, _ = find_concepts_and_attributes(test)
        for id, concept in concepts.items():
            self.assertEqual(id, "2")
            self.assertEqual(concept["prefix"], "ns")
            self.assertEqual(concept["uri"], "Class")

    def test_unnamed(self):

        test = read_drawio_xml("tests/inputs/test_unnamed.xml")
        concepts, _ = find_concepts_and_attributes(test)
        for id, concept in concepts.items():
            self.assertEqual(concept["prefix"], "")
            self.assertEqual(concept["uri"], "")

    def test_namespaces(self):

        test = read_drawio_xml("tests/inputs/test_namespaces.xml")
        namespaces = find_namespaces(test)
        for prefix, uri in namespaces.items():
            self.assertEqual(prefix in ["base", "saref"], True)
            self.assertEqual(uri in ["http://theOntology.namespace.com", "http://saref.com"], True)

    def test_intersection_1(self):

        test = read_drawio_xml("tests/inputs/test_intersection_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:intersectionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_intersection_2(self):

        test = read_drawio_xml("tests/inputs/test_intersection_2.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:intersectionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_union_1(self):

        test = read_drawio_xml("tests/inputs/test_union_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:unionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_union_2(self):

        test = read_drawio_xml("tests/inputs/test_union_2.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:unionOf")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_equivalent_1(self):

        test = read_drawio_xml("tests/inputs/test_equivalent_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:equivalentClass")
            self.assertEqual(ellipse["group"], ["3", "4"])

    def test_disjoint_1(self):

        test = read_drawio_xml("tests/inputs/test_disjoint_1.xml")
        ellipses = find_ellipses(test)
        for id, ellipse in ellipses.items():
            self.assertEqual(ellipse["type"], "owl:disjointWith")
            self.assertEqual(ellipse["group"], ["3", "4"])


if __name__ == "__main__":
    unittest.main()