from nose.tools import eq_
from korovic.background import Gradient, lerp


g = Gradient(
    [
        (0, (1, 1, 1)),
        (0.5, (1, 0, 1)),
        (1, (1, 0, 0)),
    ],
    scale=10
)

def test_gradient_stops():
    eq_(g.colour(0), (1, 1, 1))
    eq_(g.colour(5), (1, 0, 1))
    eq_(g.colour(10), (1, 0, 0))


def test_lerp():
    """Test linear interpolation of tuples"""
    a = (1, 2, 5, 7)
    b = (9, 4, 4, 3)
    eq_(lerp(0.5, a, b), (5, 3, 4.5, 5))
    eq_(lerp(0.75, a, b), (7, 3.5, 4.25, 4))


def test_gradient_interpolation():
    eq_(g.colour(2.5), (1, 0.5, 1))
    eq_(g.colour(7.5), (1, 0, 0.5))
    eq_(g.colour(8.75), (1, 0, 0.25))


def test_gradient_clamp():
    eq_(g.colour(-1), (1, 1, 1))
    eq_(g.colour(12), (1, 0, 0))
