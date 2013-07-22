#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from ..Rectangle import Rectangle, TextRectangle
from Interval import Interval, IntervalList

ROW = 0
COLUMN = 1
X = 0
Y = 1


class Cut(Rectangle):

    def __init__(self, cut_rect=None, cut_direction=None):

        self.cut_rect = cut_rect
        self.cut_direction = cut_direction

    def isxcut(self):

        return self.cut_direction == X

    def isycut(self):

        return self.cut_direction == Y

    @property
    def direction(self):

        return self.cut_direction


class BaseXYNode(object):

    def __init__(self):

        self.children = []
        self.cut = None
        self.bboxes = []


def build_xy_tree(bboxes, root=None):

    if root is None:
        root = BaseXYNode()

    x_intervals = IntervalList(*map(lambda b: Interval(b.x, b.x + b.width),
                                    bboxes))
    y_intervals = IntervalList(*map(lambda b: Interval(b.y, b.y + b.height),
                                    bboxes))

    x_gaps, y_gaps = x_intervals.gaps, y_intervlas.gaps
    world_bbox = Rectangle(x_intervals[0].begin, y_intervals[0].begin,
                           x_intervals[-1].end - x_intervals[0].begin,
                           y_intervals[-1].end - y_intervlas[0].begin)

    max_valley_size = 0
    max_valley = None
    max_valley_direction = None
    for direction, gaps in {X: x_gaps, Y: y_gaps}:
        for gap in gaps:
            if gap.length > max_valley_size:
                max_valley_size = gap.length
                max_valley = gap
                max_valley_direction = direction

    if max_valley is None:
        root.bboxes = bboxes
        return

    root.children = [BaseXYNode(), BaseXYNode()]
    bbox_group1, bbox_group2 = [], []

    if max_valley_direction == X:
        root.cut = Cut(Rectangle(max_valley.begin, world_bbox.y,
                                 max_valley.length, world_bbox.height), X)
        for bbox in bboxes:
            group = bbox_group2 if bbox.x >= max_valley.end else bbox_group1
            group.append(bbox)

    else:
        root.cut = Cut(Rectangle(world_bbox.x, max_valley.begin,
                                 world_bbox.width, max_valley.length), Y)
        for bbox in bboxes:
            group = bbox_group2 if bbox.y >= max_valley.end else bbox_group1
            group.append(bbox)

    for child in self.children:
        build_xy_tree(bbox_group1, child)

