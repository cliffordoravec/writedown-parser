import unittest

from writedown.ast import DocumentNode, LocationNode
from writedown.parser import Parser

class TestLocation(unittest.TestCase):
    def test_title(self):
        doc = Parser().parse_doc("@location Somewhere")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        loc = doc.nodes[0]
        self.assertIsInstance(loc, LocationNode)
        self.assertEqual(loc.name, "Somewhere")

if __name__ == '__main__':
    unittest.main()