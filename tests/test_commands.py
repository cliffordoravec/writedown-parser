import unittest
from typing import Generator

from writedown.ast import AuthorNode, ChapterNode, CharacterNode, CommentNode, DocumentNode, LocationNode, PartNode, PlaceNode, SceneNode, StatusNode, TagNode, TargetNode, TextNode, TitleNode, TodoNode
from writedown.commands import Commands
from writedown.parser import Parser

BOOK_PATH = "tests/books/wip.wd"

class TestCommands(unittest.TestCase):
    def test_indent(self):
        commands = Commands(None)
        self.assertEqual('', commands.indent(0))
        self.assertEqual('-- ', commands.indent(1))
        self.assertEqual('---- ', commands.indent(2))

    def test_dump(self):
        def _test_tuple(self, tuple, expected_level, expected_node_type):
            (level, node) = tuple
            self.assertEqual(expected_level, level)
            self.assertEqual(expected_node_type, type(node))

        doc = Parser().parse_doc_from_path(BOOK_PATH)
        commands = Commands(doc)
        dump = commands.export_dump()
        self.assertIsInstance(dump, Generator)
        _test_tuple(self, next(dump), 0, DocumentNode)
        _test_tuple(self, next(dump), 1, TitleNode)
        _test_tuple(self, next(dump), 1, AuthorNode)
        _test_tuple(self, next(dump), 1, CharacterNode)
        _test_tuple(self, next(dump), 1, PlaceNode)
        _test_tuple(self, next(dump), 1, PartNode)
        _test_tuple(self, next(dump), 2, TextNode)
        _test_tuple(self, next(dump), 2, ChapterNode)
        _test_tuple(self, next(dump), 3, StatusNode)
        _test_tuple(self, next(dump), 3, TargetNode)
        _test_tuple(self, next(dump), 3, TextNode)
        _test_tuple(self, next(dump), 3, SceneNode)
        _test_tuple(self, next(dump), 4, StatusNode)
        _test_tuple(self, next(dump), 4, LocationNode)
        _test_tuple(self, next(dump), 4, TodoNode)
        _test_tuple(self, next(dump), 4, TagNode)
        _test_tuple(self, next(dump), 4, CommentNode)
        _test_tuple(self, next(dump), 4, TextNode)
        _test_tuple(self, next(dump), 4, TextNode)
        _test_tuple(self, next(dump), 4, TextNode)
        _test_tuple(self, next(dump), 4, TextNode)
        _test_tuple(self, next(dump), 3, SceneNode)
        _test_tuple(self, next(dump), 4, LocationNode)
        _test_tuple(self, next(dump), 4, TodoNode)
        _test_tuple(self, next(dump), 4, TextNode)
        _test_tuple(self, next(dump), 4, TextNode)
        _test_tuple(self, next(dump), 2, ChapterNode)
        _test_tuple(self, next(dump), 3, StatusNode)
        _test_tuple(self, next(dump), 3, TargetNode)
        _test_tuple(self, next(dump), 3, TodoNode)
        _test_tuple(self, next(dump), 3, TagNode)
        _test_tuple(self, next(dump), 3, TextNode)
        _test_tuple(self, next(dump), 2, ChapterNode)
        self.assertRaises(StopIteration, lambda: next(dump))

    def test__dump(self):
        def _test_tuple(self, tuple, expected_level, expected_node_type):
            (level, node) = tuple
            self.assertEqual(expected_level, level)
            self.assertEqual(expected_node_type, type(node))

        doc = Parser().parse_doc_from_path(BOOK_PATH)
        commands = Commands(doc)
        chapters = doc.find(ChapterNode)
        chapter = next(chapters)
        dump = commands._export_dump(chapter)
        self.assertIsInstance(dump, Generator)
        _test_tuple(self, next(dump), 0, ChapterNode)
        _test_tuple(self, next(dump), 1, StatusNode)
        _test_tuple(self, next(dump), 1, TargetNode)
        _test_tuple(self, next(dump), 1, TextNode)
        _test_tuple(self, next(dump), 1, SceneNode)
        _test_tuple(self, next(dump), 2, StatusNode)
        _test_tuple(self, next(dump), 2, LocationNode)
        _test_tuple(self, next(dump), 2, TodoNode)
        _test_tuple(self, next(dump), 2, TagNode)
        _test_tuple(self, next(dump), 2, CommentNode)
        _test_tuple(self, next(dump), 2, TextNode)
        _test_tuple(self, next(dump), 2, TextNode)
        _test_tuple(self, next(dump), 2, TextNode)
        _test_tuple(self, next(dump), 2, TextNode)
        _test_tuple(self, next(dump), 1, SceneNode)
        _test_tuple(self, next(dump), 2, LocationNode)
        _test_tuple(self, next(dump), 2, TodoNode)
        _test_tuple(self, next(dump), 2, TextNode)
        _test_tuple(self, next(dump), 2, TextNode)
        self.assertRaises(StopIteration, lambda: next(dump))        

    def test_info(self):
        doc = Parser().parse_doc_from_path(BOOK_PATH)
        commands = Commands(doc)
        info = commands.info()
        self.assertIsInstance(info, Generator)
        data = '\n'.join(line for line in info)
        self.assertEqual("""A Work In Progress
by Jack Writer
1 part
3 chapters
2 scenes
2 locations
1 character
1 place
2 tags
3 todos
1 comment""", data)

if __name__ == '__main__':
    unittest.main()