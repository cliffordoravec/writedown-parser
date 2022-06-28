from datetime import date
import unittest

from writedown.ast import DocumentNode, SessionAttribute, TextNode
from writedown.parser import Parser

class TestSession(unittest.TestCase):
    def test_target(self):
        doc = Parser().parse_doc("""@session 5/1/2022
session 1
@session 5/2/2022 1000
session 2
@session 5/3/2022 1000 At the coffee shop
session 3
@session 1000 At the coffee shop
session 4
@session At the coffee shop
session 5""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 5)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertEqual(text1.text, 'session 1')
        self.assertIsInstance(text1.session, SessionAttribute)
        self.assertEqual(text1.session.date, date(2022, 5, 1))
        self.assertEqual(text1.session.target, None)
        self.assertEqual(text1.session.name, None)

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertEqual(text2.text, 'session 2')
        self.assertIsInstance(text2.session, SessionAttribute)
        self.assertEqual(text2.session.date, date(2022, 5, 2))
        self.assertEqual(text2.session.target, 1000)
        self.assertEqual(text2.session.name, None)

        text3 = doc.nodes[2]
        self.assertIsInstance(text3, TextNode)
        self.assertEqual(text3.text, 'session 3')
        self.assertIsInstance(text3.session, SessionAttribute)
        self.assertEqual(text3.session.date, date(2022, 5, 3))
        self.assertEqual(text3.session.target, 1000)
        self.assertEqual(text3.session.name, 'At the coffee shop')

        text4 = doc.nodes[3]
        self.assertIsInstance(text4, TextNode)
        self.assertEqual(text4.text, 'session 4')
        self.assertIsInstance(text4.session, SessionAttribute)
        self.assertEqual(text4.session.date, None)
        self.assertEqual(text4.session.target, 1000)
        self.assertEqual(text4.session.name, 'At the coffee shop')

        text5 = doc.nodes[4]
        self.assertIsInstance(text5, TextNode)
        self.assertEqual(text5.text, 'session 5')
        self.assertIsInstance(text5.session, SessionAttribute)
        self.assertEqual(text5.session.date, None)
        self.assertEqual(text5.session.target, None)
        self.assertEqual(text5.session.name, 'At the coffee shop')

    def test_multiple_sessions(self):
        doc = Parser().parse_doc("""@session 5/1/2022
session 1
@session 5/2/2022 At the coffee shop
session 2""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 2)

        text1 = doc.nodes[0]
        self.assertIsInstance(text1, TextNode)
        self.assertIsInstance(text1.session, SessionAttribute)
        self.assertEqual(text1.session.date, date(2022, 5, 1))
        self.assertEqual(text1.text, 'session 1')

        text2 = doc.nodes[1]
        self.assertIsInstance(text2, TextNode)
        self.assertIsInstance(text2.session, SessionAttribute)
        self.assertEqual(text2.session.date, date(2022, 5, 2))
        self.assertEqual(text2.session.name, 'At the coffee shop')
        self.assertEqual(text2.text, 'session 2')

    def test_endsession(self):
        doc = Parser().parse_doc("""@session 5/1/2022
text
@endsession""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        text = doc.nodes[0]
        self.assertIsInstance(text, TextNode)
        self.assertIsInstance(text.session, SessionAttribute)
        self.assertEqual(text.session.date, date(2022, 5, 1))
        self.assertEqual(text.text, 'text')

    def test_preserve_if_bad_format(self):
        doc = Parser().parse_doc("""@session 2022-05-01 At the coffee shop
text""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        text = doc.nodes[0]
        self.assertIsInstance(text.session, SessionAttribute)
        self.assertEqual(text.session.name, '2022-05-01 At the coffee shop')

    def test_preserve_if_bad_format_with_target(self):
        doc = Parser().parse_doc("""@session 2022-05-01 1000 At the coffee shop
text""")

        self.assertIsInstance(doc, DocumentNode)
        self.assertEqual(len(doc.nodes), 1)

        text = doc.nodes[0]
        self.assertIsInstance(text.session, SessionAttribute)
        self.assertEqual(text.session.name, '2022-05-01 At the coffee shop')
        self.assertEqual(text.session.target, 1000)

if __name__ == '__main__':
    unittest.main()