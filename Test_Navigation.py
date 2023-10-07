import unittest
from navigator import simple
from drone_types import NavigatorInput, Ring
import mocktello


class MyTestCase(unittest.TestCase):
    def test_something(self):
        inn = NavigatorInput()
        done = simple.navigate_to()
        self.assertEqual(True, done)  # add assertion here


if __name__ == '__main__':
    unittest.main()
