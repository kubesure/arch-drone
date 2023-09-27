import unittest
from drone_types import Ring, RingColor
from navigator import utils


class MyTestCase(unittest.TestCase):
    def test_shortest_path(self):
        rings = self.get_test_rings()
        is_found, ring = utils.get_short_or_longest_distance(rings, False)
        self.assertTrue(is_found)
        self.assertEqual(ring.z, 300)

    def test_longest_path(self):
        rings = self.get_test_rings()
        is_found, ring = utils.get_short_or_longest_distance(rings, True)
        self.assertTrue(is_found)
        self.assertEqual(350, ring.z)

    def test_average_distance(self):
        rings = self.get_test_rings()
        ring = utils.get_avg_distance(rings)
        print(ring)
        self.assertEqual(ring.color, RingColor.YELLOW)

    @staticmethod
    def get_test_rings():
        r1 = Ring(x=34, y=90, z=350, area=4500, color=RingColor.YELLOW)
        r2 = Ring(x=32, y=95, z=300, area=3600, color=RingColor.YELLOW)
        r3 = Ring(x=30, y=85, z=315, area=5600, color=RingColor.YELLOW)
        r4 = Ring(x=31, y=80, z=325, area=6000, color=RingColor.YELLOW)
        rings = [r1, r2, r3, r4]
        return rings


if __name__ == '__main__':
    unittest.main()
