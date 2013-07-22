#!/usr/bin/env python

# standard library imports
from collections import namedtuple

# third party related imports

# local library imports


class Point(object):
    """A utility class for point data structure.

    Attributes:
        x: A number.
        y: A number.

    """

    def __init__(self, x, y):

        self._x = x
        self._y = y

    @property
    def x(self):

        return self._x

    @property
    def y(self):

        return self._y

    def __repr__(self):
        """Get the string representation of this object."""

        return "Point(%s, %s)" % (self.x, self.y)

    def __add__(self, other):
        """Perform elementwise addition.

        >>> p1, p2 = Point(1, 2), Point(3, 4)
        >>> p1 + p2
        Point(3, 4)

        """

        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Perform elementwise subtraction.

        >>> p1, p2 = Point(1, 2), Point(3, 4)
        >>> p1 - p2
        Point(-2, -2)

        """

        return Point(self.x - other.x, self.y - other.y)

    def __neg__(self):
        """Perform elementwise negation.

        >>> p1 = Point(1, 2)
        >>> -p1
        Point(-1, -2)

        """

        return Point(-self.x, -self.y)

    def __abs__(self):
        """The distance to the origin."""

        return self.square_dist(Point(0, 0)) ** 0.5

    def square_dist(self, other=None):
        """Get the square of distance to `other`.

        Args:
            other: A Point instance.

        Returns:
            An number.

        """

        if other is None:
            other = Point(0, 0)

        dx, dy = self.x - other.x, self.y - other.y
        return dx * dx + dy * dy
