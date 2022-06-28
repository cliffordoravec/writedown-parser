import os
import unittest

from writedown.parser import Parser
from writedown.tokens import Tokens

class TestRead(unittest.TestCase):
    def _get_path(self, file):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, file)

    def test_read_str(self):
        parser = Parser()
        lines = [line for line in parser.read_str("""Line 1.
Line 2.""")]

        self.assertEqual(len(lines), 3)

        line1 = lines[0]
        self.assertEqual(line1.source, 'string')
        self.assertEqual(line1.lineno, 1)
        self.assertEqual(line1.content, "Line 1.")

        line2 = lines[1]
        self.assertEqual(line2.source, 'string')
        self.assertEqual(line2.lineno, 2)
        self.assertEqual(line2.content, "Line 2.")

        line3 = lines[2]
        self.assertEqual(line3.source, 'string')
        self.assertEqual(line3.lineno, 3)
        self.assertEqual(line3.content, Tokens.EOF)

    def test_read_file(self):
        parser = Parser()
        path = self._get_path('data/lines.wd')
        lines = [line for line in parser.read_file(path)]

        self.assertEqual(len(lines), 3)

        line1 = lines[0]
        self.assertEqual(line1.source, path)
        self.assertEqual(line1.lineno, 1)
        self.assertEqual(line1.content, "Line 1.")

        line2 = lines[1]
        self.assertEqual(line2.source, path)
        self.assertEqual(line2.lineno, 2)
        self.assertEqual(line2.content, "Line 2.")

        line3 = lines[2]
        self.assertEqual(line3.source, path)
        self.assertEqual(line3.lineno, 3)
        self.assertEqual(line3.content, Tokens.EOF)

    def test_read_bad_file(self):
        parser = Parser()
        gen = parser.read_file('data/doesnotexist.wd')
        self.assertRaises(ValueError, lambda: [line for line in gen])

if __name__ == '__main__':
    unittest.main()