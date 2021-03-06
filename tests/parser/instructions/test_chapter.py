import unittest

from writedown.ast import ChapterNode, DocumentNode
from writedown.parser import Parser

class TestChapter(unittest.TestCase):
    def test_no_number_or_title(self):
        doc = Parser().parse_doc("@chapter")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        ch = doc.nodes[0]
        self.assertIsInstance(ch, ChapterNode)
        self.assertEqual(ch.number, 1) # Autogenerated
        self.assertEqual(ch.title, None)

    def test_number_and_title(self):
        doc = Parser().parse_doc("@chapter 1 One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        ch = doc.nodes[0]
        self.assertIsInstance(ch, ChapterNode)
        self.assertEqual(ch.number, 1)
        self.assertEqual(ch.title, "One")

    def test_number(self):
        doc = Parser().parse_doc("@chapter 1")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        ch = doc.nodes[0]
        self.assertIsInstance(ch, ChapterNode)
        self.assertEqual(ch.number, 1)
        self.assertEqual(ch.title, None)

    def test_title(self):
        doc = Parser().parse_doc("@chapter One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        ch = doc.nodes[0]
        self.assertIsInstance(ch, ChapterNode)
        self.assertEqual(ch.number, 1) # Autogenerated
        self.assertEqual(ch.title, "One")

    def test_multiple(self):
        doc = Parser().parse_doc("""@chapter One
@chapter Two""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        ch1 = doc.nodes[0]
        self.assertIsInstance(ch1, ChapterNode)
        self.assertEqual(ch1.number, 1) # Autogenerated
        self.assertEqual(ch1.title, "One")

        ch2 = doc.nodes[1]
        self.assertIsInstance(ch2, ChapterNode)
        self.assertEqual(ch2.number, 2) # Autogenerated
        self.assertEqual(ch2.title, "Two")

if __name__ == '__main__':
    unittest.main()