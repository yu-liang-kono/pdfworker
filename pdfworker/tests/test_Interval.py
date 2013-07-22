#!/usr/bin/env python

# standard library imports

# third party related imports
import pytest

# local library imports
from ..Interval import Interval, IntervalList


class TestInterval(object):

    def test_intersect(self):

        i = Interval(0, 100)
        j = Interval(0, 100)
        k = i & j
        assert(k.begin == 0 and k.end == 100)

        i = Interval(0, 10)
        j = Interval(10, 20)
        k = i & j
        assert(k is None)

        i = Interval(0, 10)
        j = Interval(0, 1)
        k = i & j
        assert(k.begin == 0 and k.end == 1)

        i = Interval(0, 10)
        j = Interval(9, 10)
        k = i & j
        assert(k.begin == 9 and k.end == 10)

        i = Interval(0, 10)
        j = Interval(5, 8)
        k = i & j
        assert(k.begin == 5 and k.end == 8)

        i = Interval(0, 10)
        j = Interval(-5, 3)
        k = i & j
        assert(k.begin == 0 and k.end == 3)

        i = Interval(0, 10)
        j = Interval(-5, 15)
        k = i & j
        assert(k.begin == 0 and k.end == 10)

        i = Interval(0, 10)
        j = Interval(5, 15)
        k = i & j
        assert(k.begin == 5 and k.end == 10)

    def test_union(self):

        i = Interval(0, 10)
        j = Interval(0, 10)
        k = i | j
        assert(k.begin == 0 and k.end == 10)

        i = Interval(0, 10)
        j = Interval(15, 20)
        k = i | j
        assert(k.begin == 0 and k.end == 20)

        i = Interval(0, 10)
        j = Interval(5, 8)
        k = i | j
        assert(k.begin == 0 and k.end == 10)

        i = Interval(0, 10)
        j = Interval(5, 15)
        k = i | j
        assert(k.begin == 0 and k.end == 15)
