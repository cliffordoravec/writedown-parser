import unittest

from writedown.ast import ChapterNode, DocumentNode, SceneNode
from writedown.parser import Parser

class TestSpanningChapter(unittest.TestCase):
    def test_spanning_chapter(self):
        parser = Parser()
        doc = parser.parse_doc_from_path('tests/scenarios/spanning_chapter/data/**/*.wd')

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        ch1 = doc.nodes[0]
        self.assertIsInstance(ch1, ChapterNode)
        self.assertEqual(ch1.source, 'tests/scenarios/spanning_chapter/data/ch1/_meta.wd')
        self.assertEqual(ch1.parent, doc)
        self.assertEqual(ch1.title, "ch1")
        self.assertEqual(len(ch1.nodes), 2)

        ch1scene1 = ch1.nodes[0]
        self.assertIsInstance(ch1scene1, SceneNode)
        self.assertEqual(ch1scene1.source, 'tests/scenarios/spanning_chapter/data/ch1/scene1.wd')
        self.assertEqual(ch1scene1.parent, ch1)
        self.assertEqual(ch1scene1.title, "ch1scene1")

        ch1scene2 = ch1.nodes[1]
        self.assertIsInstance(ch1scene2, SceneNode)
        self.assertEqual(ch1scene2.source, 'tests/scenarios/spanning_chapter/data/ch1/scene2.wd')
        self.assertEqual(ch1scene2.parent, ch1)
        self.assertEqual(ch1scene2.title, "ch1scene2")

        ch2 = doc.nodes[1]
        self.assertIsInstance(ch2, ChapterNode)
        self.assertEqual(ch2.source, 'tests/scenarios/spanning_chapter/data/ch2/_meta.wd')
        self.assertEqual(ch2.parent, doc)
        self.assertEqual(ch2.title, "ch2")

        ch2scene1 = ch2.nodes[0]
        self.assertIsInstance(ch2scene1, SceneNode)
        self.assertEqual(ch2scene1.source, 'tests/scenarios/spanning_chapter/data/ch2/scene1.wd')
        self.assertEqual(ch2scene1.parent, ch2)
        self.assertEqual(ch2scene1.title, "ch2scene1")

if __name__ == '__main__':
    unittest.main()