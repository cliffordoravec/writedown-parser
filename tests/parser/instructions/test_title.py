import unittest

from writedown.ast import DocumentNode, TitleNode
from writedown.parser import Parser

class TestTitle(unittest.TestCase):
    def test_title(self):
        doc = Parser().parse_doc("@title My title")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        title = doc.nodes[0]
        self.assertIsInstance(title, TitleNode)
        self.assertEqual(title.text, "My title")

if __name__ == '__main__':
    unittest.main()