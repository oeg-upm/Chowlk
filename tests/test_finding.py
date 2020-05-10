import unittest
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from modules.finding import *
from modules.utils import read_drawio_xml

class TestConcepts(unittest.TestCase):
    def test_concept_structure(self):
        """
        Test that the structure of the concept found is correct
        """
        data = read_drawio_xml("tests/inputs/test_concept_structure.xml")
        concepts, _ = find_concepts_and_attributes(data)
        for id, concept in concepts.items():
            self.assertEqual(id, "2")
            self.assertEqual(concept["prefix"], "ns")
            self.assertEqual(concept["uri"], "Class")

if __name__ == "__main__":
    unittest.main()