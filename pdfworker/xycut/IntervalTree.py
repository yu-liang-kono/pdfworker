#!/usrbin/env python

# standard library imports

# third party related imports

# local library imports


class Interval(object):

    def __init__(self, begin, end):

        self.begin = begin
        self.end = end

    def intersect(self, other):

        return self & other

    def __and__(self, other):

        if other.begin < self.begin:
            if other.end <= self.begin:
                return None
            elif other.end >= self.end:
                return Interval(self.begin, self.end)

            return Interval(other.end, self.begin)

        elif other.begin <= self.end:
            if other.end <= self.end:
                return Interval(other.begin, other.end)

            return Interval(other.begin, self.end)

        return None

    def union(self, other):

        return self | other

    def __or__(self, other):

        return Interval(min(self.begin, other.begin),
                        max(self.end, other.end))


class IntervalList(object):

    def __init__(self, *intervals):

        self.intervals = []
        map(self.add, intervals)

    def __len__(self):

        return len(self.intervals)

    def add(self, interval):

        return
