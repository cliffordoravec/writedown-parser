import unittest

from writedown.ast import DocumentNode, TextNode
from writedown.parser import Parser

class TestInclude(unittest.TestCase):
    def test_single_target(self):
        doc = Parser().parse_doc("@include tests/parser/instructions/data/include/dir/file1.wd")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        text = doc.nodes[0]
        self.assertIsInstance(text, TextNode)
        self.assertEqual(text.source, "tests/parser/instructions/data/include/dir/file1.wd")
        self.assertEqual(text.text, "File One")

    def test_multi_target(self):
        doc = Parser().parse_doc("@include tests/parser/instructions/data/include/dir/**/*.wd")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 4)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.source, "tests/parser/instructions/data/include/dir/file1.wd")
        self.assertEqual(text1.text, "File One")

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.source, "tests/parser/instructions/data/include/dir/file3.wd")
        self.assertEqual(text2.text, "File Three")

        text3 = doc.nodes[2]
        self.assertIsInstance(text3, TextNode)
        self.assertEqual(text3.source, "tests/parser/instructions/data/include/dir/subdir/file4.wd")
        self.assertEqual(text3.text, "File Four")

        text4 = doc.nodes[3]
        self.assertIsInstance(text4, TextNode)
        self.assertEqual(text4.source, "tests/parser/instructions/data/include/dir/subdir/file6.wd")
        self.assertEqual(text4.text, "File Six")

    def test_bad(self):
        self.assertRaises(ValueError, lambda: Parser().parse_doc("@include tests/parser/instructions/data/include/nosuchfile.wd"))

    def test_file(self):
        doc = Parser().parse_doc("@include tests/parser/instructions/data/include/include.wd")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.source, "tests/parser/instructions/data/include/dir/subdir/file6.wd")
        self.assertEqual(text1.text, "File Six")

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.source, "tests/parser/instructions/data/include/dir/file3.wd")
        self.assertEqual(text2.text, "File Three")

    def test_nested(self):
        doc = Parser().parse_doc("@include tests/parser/instructions/data/include/nested/**/include.wd")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 3)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.source, "tests/parser/instructions/data/include/nested/subdir/include.wd")
        self.assertEqual(text1.text, "Include")

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.source, "tests/parser/instructions/data/include/nested/subdir/../filea.wd")
        self.assertEqual(text2.text, "File A")

        text3 = doc.nodes[2]
        self.assertIsInstance(text3, TextNode)
        self.assertEqual(text3.source, "tests/parser/instructions/data/include/nested/subdir/../subdir2/fileb.wd")
        self.assertEqual(text3.text, "File B")

if __name__ == '__main__':
    unittest.main()