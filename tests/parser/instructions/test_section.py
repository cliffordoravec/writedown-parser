import unittest

from writedown.ast import DocumentNode, SectionNode
from writedown.parser import Parser

class TestSection(unittest.TestCase):
    def test_no_number_or_title(self):
        doc = Parser().parse_doc("@section")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        section = doc.nodes[0]
        self.assertIsInstance(section, SectionNode)
        self.assertEqual(section.number, None)
        self.assertEqual(section.title, None)

    def test_number_and_title(self):
        doc = Parser().parse_doc("@section 1 One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        section = doc.nodes[0]
        self.assertIsInstance(section, SectionNode)
        self.assertEqual(section.number, 1)
        self.assertEqual(section.title, "One")

    def test_ext_number_and_title(self):
        doc = Parser().parse_doc("@section 1.1 One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        section = doc.nodes[0]
        self.assertIsInstance(section, SectionNode)
        self.assertEqual(section.number, '1.1')
        self.assertEqual(section.title, "One")

    def test_number(self):
        doc = Parser().parse_doc("@section 1")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        section = doc.nodes[0]
        self.assertIsInstance(section, SectionNode)
        self.assertEqual(section.number, 1)
        self.assertEqual(section.title, None)

    def test_title(self):
        doc = Parser().parse_doc("@section One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        section = doc.nodes[0]
        self.assertIsInstance(section, SectionNode)
        self.assertEqual(section.number, None)
        self.assertEqual(section.title, "One")

if __name__ == '__main__':
    unittest.main()