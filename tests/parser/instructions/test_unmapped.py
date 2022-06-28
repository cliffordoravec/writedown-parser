import unittest

from writedown.ast import DocumentNode, UnmappedInstructionNode
from writedown.parser import Parser

class TestUnmapped(unittest.TestCase):
    def test_todo(self):
        doc = Parser().parse_doc("@doesntexist An unmapped instruction")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        node = doc.nodes[0]
        self.assertIsInstance(node, UnmappedInstructionNode)
        self.assertEqual(node.instruction, "@doesntexist")
        self.assertEqual(node.text, "An unmapped instruction")

if __name__ == '__main__':
    unittest.main()