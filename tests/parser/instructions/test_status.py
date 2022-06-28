import unittest

from writedown.ast import DocumentNode, StatusNode
from writedown.parser import Parser

class TestStatus(unittest.TestCase):
    def test_new(self):
        doc = Parser().parse_doc("@status new")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        status = doc.nodes[0]
        self.assertIsInstance(status, StatusNode)
        self.assertEqual(status.status, StatusNode.Statuses.NEW)

    def test_draft(self):
        doc = Parser().parse_doc("@status draft")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        status = doc.nodes[0]
        self.assertIsInstance(status, StatusNode)
        self.assertEqual(status.status, StatusNode.Statuses.DRAFT) 

    def test_revision(self):
        doc = Parser().parse_doc("@status revision")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        status = doc.nodes[0]
        self.assertIsInstance(status, StatusNode)
        self.assertEqual(status.status, StatusNode.Statuses.REVISION)

    def test_done(self):
        doc = Parser().parse_doc("@status done")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        status = doc.nodes[0]
        self.assertIsInstance(status, StatusNode)
        self.assertEqual(status.status, StatusNode.Statuses.DONE)

    def test_bad(self):
        self.assertRaises(ValueError, lambda: Parser().parse_doc("@status bad"))

if __name__ == '__main__':
    unittest.main()