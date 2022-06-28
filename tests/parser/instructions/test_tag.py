import unittest

from writedown.ast import DocumentNode, TagNode
from writedown.parser import Parser

class TestTag(unittest.TestCase):
    def test_tag(self):
        doc = Parser().parse_doc("@tag atag")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        tag = doc.nodes[0]
        self.assertIsInstance(tag, TagNode)
        self.assertEqual(len(tag.tags), 1)
        self.assertEqual(tag.tags[0], 'atag')

    def test_tags(self):
        doc = Parser().parse_doc("@tag one two")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        tag = doc.nodes[0]
        self.assertIsInstance(tag, TagNode)
        self.assertEqual(len(tag.tags), 2)
        self.assertEqual(tag.tags[0], 'one')
        self.assertEqual(tag.tags[1], 'two')

if __name__ == '__main__':
    unittest.main()