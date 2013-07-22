#!/usr/bin/env

# standard library imports
import random

# third party related imports
import pytest

# local library imports
from ..Rectangle import Rectangle


class TestRectangle(object):

    def test_area(self):

        r = Rectangle(0, 0, 1, 1)
        assert(r.area == 1)

    def test_vertices(self):

        r = Rectangle(random.randint(0, 65535),
                      random.randint(0, 65535),
                      random.randint(0, 65535),
                      random.randint(0, 65535))
        assert(r.vertices[0].x == r.x)
        assert(r.vertices[0].y == r.y)
        assert(r.vertices[1].x == r.x + r.w)
        assert(r.vertices[1].y == r.y)
        assert(r.vertices[2].x == r.x + r.w)
        assert(r.vertices[2].y == r.y + r.h)
        assert(r.vertices[3].x == r.x)
        assert(r.vertices[3].y == r.y + r.h)

    def test_distance(self):

        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(11, 11, 10, 10)
        assert(r1.distance(r2), 2)

        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(1, 1, 9, 9)
        assert(r1.distance(r2) == 0)

    def test_intersect(self):

        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(10, 10, 10, 10)
        expected = None
        assert(r1.intersect(r2) is None)
        assert(r2.intersect(r1) is None)
        assert(r1 & r2 is None)
        r1 &= r2
        assert(r1 is None)

        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(5, 5, 10, 10)
        expected = Rectangle(5, 5, 5, 5)
        assert(r1.intersect(r2) == expected)
        assert(r2.intersect(r1) == expected)
        assert(r1 & r2 == expected)
        r1 &= r2
        assert(r1 == expected)

    def test_union(self):

        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(10, 10, 10, 10)
        expected = Rectangle(0, 0, 20, 20)
        assert(r1.union(r2) == expected)
        assert(r2.union(r1) == expected)
        assert(r1 | r2 == expected)
        r1 |= r2
        assert(r1 == expected)

        r1 = Rectangle(0, 0, 10, 10)
        expected = Rectangle(0, 0, 10, 10)
        assert(r1.union(r1) == expected)
        assert(r1 | r1 == expected)
        r1 |= r1
        assert(r1 == expected)

        r1 = Rectangle(5, 5, 10, 10)
        r2 = Rectangle(0, 0, 10, 10)
        expected = Rectangle(0, 0, 15, 15)
        assert(r1.union(r2) == expected)
        assert(r2.union(r1) == expected)
        assert(r1 | r2 == expected)
        r1 |= r2
        assert(r1 == expected)

