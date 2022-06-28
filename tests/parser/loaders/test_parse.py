import os
import unittest

from writedown.ast import DocumentNode, TextNode
from writedown.parser import Parser

class TestParse(unittest.TestCase):
    def _get_path(self, file):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, file)

    def test_parse_file(self):
        parser = Parser()
        path = self._get_path('data/lines.wd')
        nodes = parser.parse_file(path)
        self.assertEqual(len(nodes), 2)

        text1 = nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.text, 'Line 1.')

        text2 = nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.text, 'Line 2.')   

    def test_parse_path(self):
        parser = Parser()
        nodes = parser.parse_path('tests/parser/loaders/data/dir/**/*.wd')
        self.assertEqual(len(nodes), 2)

        text1 = nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.source, 'tests/parser/loaders/data/dir/file1.wd')
        self.assertEqual(text1.text, 'File 1')

        text2 = nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.source, 'tests/parser/loaders/data/dir/subdir/file3.wd')
        self.assertEqual(text2.text, 'File 3')

    def test_parse_doc(self):
        parser = Parser()
        doc = parser.parse_doc("""Line 1.
Line 2.""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.text, "Line 1.")

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.text, "Line 2.")

    def test_parse_doc_from_path_single_file(self):
        parser = Parser()
        doc = parser.parse_doc_from_path('tests/parser/loaders/data/lines.wd')

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.text, "Line 1.")

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.text, "Line 2.")

if __name__ == '__main__':
    unittest.main()