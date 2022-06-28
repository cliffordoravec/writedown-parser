import unittest

from writedown.ast import CommentNode, DocumentNode 
from writedown.parser import Parser

class TestComments(unittest.TestCase):
    def test_comment(self):
        doc = Parser().parse_doc("@comment a comment")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        comment = doc.nodes[0]
        self.assertIsInstance(comment, CommentNode)
        self.assertEqual(comment.comment, "a comment")

    def test_shorthand(self):
        doc = Parser().parse_doc("@# a comment")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        comment = doc.nodes[0]
        self.assertIsInstance(comment, CommentNode)
        self.assertEqual(comment.comment, "a comment")

    def test_single_line_block(self):
        doc = Parser().parse_doc("@* a single-line comment *@")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        comment = doc.nodes[0]
        self.assertIsInstance(comment, CommentNode)
        self.assertEqual(comment.comment, "a single-line comment")

    def test_many_single_line_blocks(self):
        doc = Parser().parse_doc("""@* a single-line comment *@
@* another single-line comment *@""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        comment1 = doc.nodes[0]
        self.assertIsInstance(comment1, CommentNode)
        self.assertEqual(comment1.comment, "a single-line comment")

        comment2 = doc.nodes[1]
        self.assertIsInstance(comment2, CommentNode)
        self.assertEqual(comment2.comment, "another single-line comment")

    def test_multi_line_block(self):
        doc = Parser().parse_doc("""@* a 
multi-line 
comment 
*@""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        comment = doc.nodes[0]
        self.assertIsInstance(comment, CommentNode)
        self.assertEqual(comment.comment, """a
multi-line
comment""")

    def test_many_multi_line_blocks(self):
        doc = Parser().parse_doc("""@* a 
multi-line 
comment 
*@
@*
    another
    multi-line
    comment *@""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        comment1 = doc.nodes[0]
        self.assertIsInstance(comment1, CommentNode)
        self.assertEqual(comment1.comment, """a
multi-line
comment""")

        comment2 = doc.nodes[1]
        self.assertIsInstance(comment2, CommentNode)
        self.assertEqual(comment2.comment, """another
multi-line
comment""")

if __name__ == '__main__':
    unittest.main()