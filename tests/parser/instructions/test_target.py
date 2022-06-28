import unittest

from writedown.ast import DocumentNode, TargetNode
from writedown.parser import Parser

class TestTarget(unittest.TestCase):
    def test_target(self):
        doc = Parser().parse_doc("@target 1000")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        target = doc.nodes[0]
        self.assertIsInstance(target, TargetNode)
        self.assertEqual(target.value, 1000)

if __name__ == '__main__':
    unittest.main()