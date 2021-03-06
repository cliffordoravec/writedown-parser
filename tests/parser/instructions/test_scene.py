import unittest

from writedown.ast import DocumentNode, SceneNode
from writedown.parser import Parser

class TestScene(unittest.TestCase):
    def test_no_number_or_title(self):
        doc = Parser().parse_doc("@scene")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        scene = doc.nodes[0]
        self.assertIsInstance(scene, SceneNode)
        self.assertEqual(scene.number, 1) # Autogenerated
        self.assertEqual(scene.title, None)

    def test_number_and_title(self):
        doc = Parser().parse_doc("@scene 1 One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        scene = doc.nodes[0]
        self.assertIsInstance(scene, SceneNode)
        self.assertEqual(scene.number, 1)
        self.assertEqual(scene.title, "One")

    def test_number(self):
        doc = Parser().parse_doc("@scene 1")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        scene = doc.nodes[0]
        self.assertIsInstance(scene, SceneNode)
        self.assertEqual(scene.number, 1)
        self.assertEqual(scene.title, None)

    def test_title(self):
        doc = Parser().parse_doc("@scene One")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        scene = doc.nodes[0]
        self.assertIsInstance(scene, SceneNode)
        self.assertEqual(scene.number, 1) # Autogenerated
        self.assertEqual(scene.title, "One")

    def test_multiple(self):
        doc = Parser().parse_doc("""@scene One
@scene Two""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        scene1 = doc.nodes[0]
        self.assertIsInstance(scene1, SceneNode)
        self.assertEqual(scene1.number, 1) # Autogenerated
        self.assertEqual(scene1.title, "One")

        scene2 = doc.nodes[1]
        self.assertIsInstance(scene2, SceneNode)
        self.assertEqual(scene2.number, 2) # Autogenerated
        self.assertEqual(scene2.title, "Two")        

if __name__ == '__main__':
    unittest.main()