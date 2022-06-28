import unittest

from writedown.buffer import IndexedGeneratorBuffer

class TestIndexedGeneratorBuffer(unittest.TestCase):
    def test_read(self):
        def _test_data():
            yield "one"
            yield "two"
            yield "three"

        buffer = IndexedGeneratorBuffer(_test_data())

        buffer.read()
        self.assertEqual(["one"], buffer.buffer)
        self.assertEqual(1, buffer.consumed)
        self.assertEqual(0, buffer.offset)

        buffer.read(2)
        self.assertEqual(["one", "two", "three"], buffer.buffer)
        self.assertEqual(3, buffer.consumed)
        self.assertEqual(0, buffer.offset)
        self.assertRaises(StopIteration, lambda: buffer.read())

    def test_get(self):
        def _test_data():
            yield "one"
            yield "two"
            yield "three"

        buffer = IndexedGeneratorBuffer(_test_data())
        self.assertRaises(IndexError, lambda: buffer.get(-1))
        self.assertEqual("one", buffer.get(0))
        self.assertEqual("two", buffer.get(1))
        self.assertEqual("three", buffer.get(2))
        self.assertRaises(StopIteration, lambda: buffer.get(3))

    def test_truncate(self):
        def _test_data():
            yield "one"
            yield "two"
            yield "three"
            yield "four"

        buffer = IndexedGeneratorBuffer(_test_data())

        buffer.read()
        self.assertEqual(["one"], buffer.buffer)
        self.assertEqual(0, buffer.offset)
        self.assertEqual("one", buffer.get(0))

        buffer.truncate(1)
        self.assertEqual([], buffer.buffer)
        self.assertEqual(1, buffer.offset)
        self.assertRaises(IndexError, lambda: buffer.get(0))

        buffer.read()
        self.assertEqual(["two"], buffer.buffer)
        self.assertEqual(1, buffer.offset)
        self.assertRaises(IndexError, lambda: buffer.get(0))
        self.assertEqual("two", buffer.get(1))

        buffer.read()
        self.assertEqual(["two", "three"], buffer.buffer)
        self.assertEqual(1, buffer.offset)
        self.assertRaises(IndexError, lambda: buffer.get(0))
        self.assertEqual("two", buffer.get(1))
        self.assertEqual("three", buffer.get(2))

        buffer.truncate(2)
        self.assertEqual(["three"], buffer.buffer)
        self.assertEqual(2, buffer.offset)
        self.assertRaises(IndexError, lambda: buffer.get(0))
        self.assertRaises(IndexError, lambda: buffer.get(1))
        self.assertEqual("three", buffer.get(2))

        buffer.read()
        self.assertEqual(["three", "four"], buffer.buffer)
        self.assertEqual(2, buffer.offset)
        self.assertRaises(IndexError, lambda: buffer.get(0))
        self.assertRaises(IndexError, lambda: buffer.get(1))
        self.assertEqual("three", buffer.get(2))
        self.assertEqual("four", buffer.get(3))

        buffer.truncate(4)
        self.assertEqual([], buffer.buffer)
        self.assertEqual(4, buffer.offset)
        self.assertRaises(IndexError, lambda: buffer.get(0))
        self.assertRaises(IndexError, lambda: buffer.get(1))
        self.assertRaises(IndexError, lambda: buffer.get(2))
        self.assertRaises(IndexError, lambda: buffer.get(3))

    def test_valid_index(self):
        def _test_data():
            yield "one"
            yield "two"
            yield "three"

        buffer = IndexedGeneratorBuffer(_test_data())
        self.assertTrue(buffer.valid_index(0))
        self.assertTrue(buffer.valid_index(1))
        self.assertTrue(buffer.valid_index(2))
        self.assertFalse(buffer.valid_index(3)) 

if __name__ == '__main__':
    unittest.main()