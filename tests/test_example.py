import unittest

class TestExample(unittest.TestCase):
    def test_functionality_1(self):
        self.assertEqual(1 + 1, 2)

    def test_functionality_2(self):
        self.assertTrue(isinstance("hello", str))

    def test_functionality_3(self):
        self.assertIn(3, [1, 2, 3])

if __name__ == '__main__':
    unittest.main()