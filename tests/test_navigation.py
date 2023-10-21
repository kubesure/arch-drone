import unittest
from drone_types import Direction
import constants
from navigator import simple


class MyTestCase(unittest.TestCase):

    def test_direction_right(self):
        direction = simple.get_left_right_direction(48, constants.right_left_threshold)
        self.assertEqual(direction, Direction.RIGHT)

    def test_direction_left(self):
        direction = simple.get_left_right_direction(-48, constants.right_left_threshold)
        self.assertEqual(direction, Direction.LEFT)

    def test_direction_center(self):
        direction = simple.get_left_right_direction(0, constants.right_left_threshold)
        self.assertEqual(direction, Direction.CENTER)


if __name__ == '__main__':
    unittest.main()
