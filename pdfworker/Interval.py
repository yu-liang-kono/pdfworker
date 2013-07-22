#!/usrbin/env python

# standard library imports
from operator import itemgetter

# third party related imports

# local library imports


class Interval(object):

    def __init__(self, begin, end):

        self.begin = begin
        self.end = end

    def __repr__(self):

        return 'Interval<%s, %s>' % (self.begin, self.end)

    def intersect(self, other):

        return self & other

    def __and__(self, other):

        if other.begin < self.begin:
            if other.end <= self.begin:
                return None
            elif other.end >= self.end:
                return Interval(self.begin, self.end)

            return Interval(self.begin, other.end)

        elif other.begin < self.end:
            if other.end <= self.end:
                return Interval(other.begin, other.end)

            return Interval(other.begin, self.end)

        return None

    def union(self, other):

        return self | other

    def __or__(self, other):

        return Interval(min(self.begin, other.begin),
                        max(self.end, other.end))

    @property
    def length(self):

        return self.end - self.begin

    def __eq__(self, other):

        return self.begin == other.begin and self.end == other.end


class IntervalList(object):

    def __init__(self, *intervals):

        self.dirty = False
        self.intervals = []
        map(self.add, intervals)

    def __len__(self):

        self._ensure_clean()
        return len(self.intervals)

    def add(self, interval):

        self.dirty = True
        self.intervals.append(interval)

    def __getitem__(self, ix):

        self._ensure_clean()
        return self.intervals[ix]

    def _ensure_clean(self):

        if self.dirty:
            self._digest()
            self.dirty = False

    def _digest(self):

        if len(self.intervals) <= 1:
            return

        endpoints = map(lambda i: (i.begin, 0), self.intervals)
        endpoints.extend(map(lambda i: (i.end, 1), self.intervals))
        endpoints = sorted(endpoints, key=itemgetter(0, 1))

        self.intervals = []
        interval = Interval(endpoints[0][0], None)
        counter = 1
        for ix in xrange(1, len(endpoints)):
            counter += 1 if endpoints[ix][1] == 0 else -1

            if counter == 0:
                interval.end = endpoints[ix][0]
                self.intervals.append(interval)
                if ix + 1 < len(endpoints):
                    interval = Interval(endpoints[ix + 1][0], None)

    @property
    def gaps(self):

        self._ensure_clean()

        if len(self.intervals) <= 1:
            return []

        ret = []
        for ix in xrange(1, len(self.intervals)):
            ret.append(Interval(self.intervals[ix - 1].end,
                                self.intervals[ix].begin))

        return ret

