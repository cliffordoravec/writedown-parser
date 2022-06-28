import unittest

from writedown.ast import DocumentNode, TodoNode
from writedown.parser import Parser

class TestTodo(unittest.TestCase):
    def test_todo(self):
        doc = Parser().parse_doc("@todo My todo")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        todo = doc.nodes[0]
        self.assertIsInstance(todo, TodoNode)
        self.assertEqual(todo.text, "My todo")

if __name__ == '__main__':
    unittest.main()