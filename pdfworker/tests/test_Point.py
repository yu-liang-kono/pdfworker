#!/usr/bin/env

# standard library imports
import random

# third party related imports
import pytest

# local library imports
from ..Point import Point


class TestPoint(object):

    def _get_rand_point(self):

        return Point(random.randint(0, 65535), random.randint(0, 65535))

    def test_add(self):

        p1 = self._get_rand_point()
        p2 = self._get_rand_point()
        p3 = p1 + p2

        assert(p3.x == p1.x + p2.x)
        assert(p3.y == p1.y + p2.y)

    def test_sub(self):

        p1, p2 = self._get_rand_point(), self._get_rand_point()
        p3 = p1 - p2

        assert(p3.x == p1.x - p2.x)
        assert(p3.y == p1.y - p2.y)

    def test_neg(self):

        p = self._get_rand_point()
        pp = -p
        assert(pp.x == -p.x)
        assert(pp.y == -p.y)

    def test_square_dist(self):

        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert(p1.square_dist(p2) == 25)
        assert(p2.square_dist(p1) == 25)

    def test_abs(self):

        p1 = Point(3, 4)
        assert(abs(p1) == 5)
