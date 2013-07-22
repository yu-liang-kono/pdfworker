#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from ..Interval import Interval, IntervalList


class TestIntervalList(object):

    def test_add(self):

        intv_list = IntervalList()
        intv_list.add(Interval(0, 10))
        intv_list.add(Interval(10, 20))
        assert(len(intv_list) == 1)
        assert(intv_list[0].begin == 0)
        assert(intv_list[0].end == 20)

        intv_list = IntervalList()
        intv_list.add(Interval(0, 10))
        intv_list.add(Interval(15, 20))
        intv_list.add(Interval(9, 11))
        assert(len(intv_list) == 2)
        assert(intv_list[0] == Interval(0, 11))
        assert(intv_list[1] == Interval(15, 20))

        intv_list = IntervalList()
        intv_list.add(Interval(40, 50))
        intv_list.add(Interval(20, 30))
        intv_list.add(Interval(0, 10))
        assert(len(intv_list) == 3)
        assert(intv_list[0] == Interval(0, 10))
        assert(intv_list[1] == Interval(20, 30))
        assert(intv_list[2] == Interval(40, 50))

    def test_gaps(self):

        intv_list = IntervalList()
        assert(len(intv_list.gaps) == 0)

        intv_list.add(Interval(0, 10))
        intv_list.add(Interval(10, 20))
        assert(len(intv_list.gaps) == 0)

        intv_list = IntervalList()
        intv_list.add(Interval(40, 50))
        intv_list.add(Interval(20, 30))
        intv_list.add(Interval(0, 10))
        assert(len(intv_list.gaps) == 2)
        assert(intv_list.gaps[0] == Interval(10, 20))
        assert(intv_list.gaps[1] == Interval(30, 40))
