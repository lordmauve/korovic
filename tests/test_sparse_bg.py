from nose.tools import eq_
from unittest import TestCase
from korovic.camera import Rect
from korovic.vector import v
from korovic.background import Clouds, SpatialSparseHash

def set_eq(s1, s2):
    assert s1 == s2, """s2 - s1 == %r\ns1 - s2 == %r""" % (
        s2 - s1,
        s1 - s2
    )

class SparseHashTest(TestCase):
    def coords_test(self):
        """Viewport is correctly split into cells"""
        h = SpatialSparseHash(cell_size=100)
        vp = Rect((10, -20), (190, 20))
        cs = h._cells(vp)

        expectation = set([
            (0, -100),
            (100, -100),
            (0, 0),
            (100, 0)
        ])
        set_eq(set(cs), expectation)

        # Expectation doesn't change if we end on a cell boundary
        vp = Rect((10, -20), (200, 100))
        cs2 = h._cells(vp)
        set_eq(set(cs2), expectation)

    def cell_test(self):
        """We can get rects for each cell in a viewport"""
        h = SpatialSparseHash(cell_size=100)
        vp = Rect((10, -20), (190, 20))
        cs = h._cell_rects(vp)

        expectation = set([
            Rect((0, -100), (100, 0)),
            Rect((100, -100), (200, 0)),
            Rect((0, 0), (100, 100)),
            Rect((100, 0), (200, 100)),
        ])
        set_eq(set(cs), expectation)

        # Expectation doesn't change if we end on a cell boundary
        vp = Rect((10, -20), (200, 100))
        cs2 = h._cell_rects(vp)
        set_eq(set(cs2), expectation)


class CloudsTest(TestCase):
    def setUp(self):
        Clouds.load()
        self.clouds = Clouds()
        self.viewport = self.get_viewport((7000, 500))

    def get_viewport(self, offset=v(0, 0), size=v(800, 600)):
        return Rect(v(offset), v(offset) + size)
    
    def get_clouds(self, offset=v(0, 0), size=v(800, 600)):
        vp = self.get_viewport(offset, size)
        return self.clouds.for_viewport(vp)

    def test_clouds(self):
        """Test that a few random viewports all contain clouds."""
        assert list(self.get_clouds((4750, 300)))
        assert list(self.get_clouds((1000, 2000)))
    
    def test_no_clouds_sea_level(self):
        """Test that there are no clouds below a certain ceiling"""
        assert not list(self.get_clouds(size=v(4000, 400)))

    def test_no_clouds_space(self):
        """Test that there are no clouds in space"""
        assert not list(self.get_clouds(offset=v(0, 50000), size=v(4000, 1000)))

    def test_persistence(self):
        positions = [c.position for c in self.clouds.for_viewport(self.viewport)]
        pos2 = [c.position for c in Clouds().for_viewport(self.viewport)]
        assert positions == pos2
