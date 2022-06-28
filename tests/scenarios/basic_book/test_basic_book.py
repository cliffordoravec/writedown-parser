import unittest

from writedown.ast import AuthorNode, ChapterNode, DocumentNode, SceneNode, TitleNode, TextNode
from writedown.parser import Parser

class TestBasicBook(unittest.TestCase):
    def test_basic_book(self):
        parser = Parser()
        doc = parser.parse_doc_from_path('tests/scenarios/basic_book/data/**/*.wd')

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 4)

        title = doc.nodes[0]
        self.assertIsInstance(title, TitleNode)
        self.assertEqual(title.source, 'tests/scenarios/basic_book/data/_meta.wd')
        self.assertEqual(title.parent, doc)
        self.assertEqual(title.text, "Book Title")

        author = doc.nodes[1]
        self.assertIsInstance(author, AuthorNode)
        self.assertEqual(author.source, 'tests/scenarios/basic_book/data/_meta.wd')
        self.assertEqual(author.parent, doc)
        self.assertEqual(author.name, "Book Author")

        ch1 = doc.nodes[2]
        self.assertIsInstance(ch1, ChapterNode)
        self.assertEqual(ch1.source, 'tests/scenarios/basic_book/data/ch1.wd')
        self.assertEqual(ch1.parent, doc)
        self.assertEqual(ch1.number, 1)
        self.assertEqual(ch1.title, "One")
        self.assertEqual(len(ch1.nodes), 2)

        ch1scene1 = ch1.nodes[0]
        self.assertIsInstance(ch1scene1, SceneNode)
        self.assertEqual(ch1scene1.source, 'tests/scenarios/basic_book/data/ch1.wd')
        self.assertEqual(ch1scene1.parent, ch1)
        self.assertEqual(ch1scene1.number, 1)
        self.assertEqual(ch1scene1.title, "One")
        self.assertEqual(len(ch1scene1.nodes), 1)

        ch1scene1text = ch1scene1.nodes[0]
        self.assertIsInstance(ch1scene1text, TextNode)
        self.assertEqual(ch1scene1text.source, 'tests/scenarios/basic_book/data/ch1.wd')
        self.assertEqual(ch1scene1text.parent, ch1scene1)
        self.assertEqual(ch1scene1text.text, "Text in chapter one scene one.")

        ch1scene2 = ch1.nodes[1]
        self.assertIsInstance(ch1scene2, SceneNode)
        self.assertEqual(ch1scene2.source, 'tests/scenarios/basic_book/data/ch1.wd')
        self.assertEqual(ch1scene2.parent, ch1)
        self.assertEqual(ch1scene2.number, 2)
        self.assertEqual(ch1scene2.title, "Two")
        self.assertEqual(len(ch1scene2.nodes), 1)

        ch1scene2text = ch1scene2.nodes[0]
        self.assertIsInstance(ch1scene2text, TextNode)
        self.assertEqual(ch1scene2text.source, 'tests/scenarios/basic_book/data/ch1.wd')
        self.assertEqual(ch1scene2text.parent, ch1scene2)
        self.assertEqual(ch1scene2text.text, "Text in chapter one scene two.")

        ch2 = doc.nodes[3]
        self.assertIsInstance(ch2, ChapterNode)
        self.assertEqual(ch2.source, 'tests/scenarios/basic_book/data/ch2.wd')
        self.assertEqual(ch2.parent, doc)
        self.assertEqual(ch2.number, 2)
        self.assertEqual(ch2.title, "Two")

        ch2scene1 = ch2.nodes[0]
        self.assertIsInstance(ch2scene1, SceneNode)
        self.assertEqual(ch2scene1.source, 'tests/scenarios/basic_book/data/ch2.wd')
        self.assertEqual(ch2scene1.parent, ch2)
        self.assertEqual(ch2scene1.number, 1)
        self.assertEqual(ch2scene1.title, "One")
        self.assertEqual(len(ch2scene1.nodes), 1)

        ch2scene1text = ch2scene1.nodes[0]
        self.assertIsInstance(ch2scene1text, TextNode)
        self.assertEqual(ch2scene1text.source, 'tests/scenarios/basic_book/data/ch2.wd')
        self.assertEqual(ch2scene1text.parent, ch2scene1)
        self.assertEqual(ch2scene1text.text, "Text in chapter two scene one.")

        ch2scene2 = ch2.nodes[1]
        self.assertIsInstance(ch2scene2, SceneNode)
        self.assertEqual(ch2scene2.source, 'tests/scenarios/basic_book/data/ch2.wd')
        self.assertEqual(ch2scene2.parent, ch2)
        self.assertEqual(ch2scene2.number, 2)
        self.assertEqual(ch2scene2.title, "Two")
        self.assertEqual(len(ch2scene2.nodes), 1)

        ch2scene2text = ch2scene2.nodes[0]
        self.assertIsInstance(ch2scene2text, TextNode)
        self.assertEqual(ch2scene2text.source, 'tests/scenarios/basic_book/data/ch2.wd')
        self.assertEqual(ch2scene2text.parent, ch2scene2)
        self.assertEqual(ch2scene2text.text, "Text in chapter two scene two.")

if __name__ == '__main__':
    unittest.main()