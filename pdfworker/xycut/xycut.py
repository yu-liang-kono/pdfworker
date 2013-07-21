#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


ROW = 0
COLUMN = 1
X = 0
Y = 1


class Cut(Rectangle):

    def __init__(self):

        self.cut_rect = None
        self.cut_direction = None

    def isxcut(self):

        return self.cut_direction == X

    def isycut(self):

        return self.cut_direction == Y


class BaseXYNode(object):

    def __init__(self, reading_order):

        self.children = []
        self.reading_order = reading_order
        self.cut = None

    def visit(self):

        return True

    def traverse(self):

        if self.isleaf():
            self.visit()
            return

        if  (self.reading_order == ROW and self.cut.isxcut()) or \
            (self.reading_order == COLUMN and self.cut.isycut()):
            map(lambda child: child.traverse(), self.children)
        else:
            map(lambda child: child.traverse(), reverse(self.children))


def build_xy_tree(bboxes, reading_order):

    root = XYNode(init_orientation)
    xy_cut(root, world, bboxes, reading_order)
    return root

def xy_cut(root, bboxes, cut_direction):

    if cut_direction == X:
        x_cut(root, bboxes)
    else:
        y_cut(root, bboxes)

def x_cut(root, bboxes):

    root.orientation = ROW
    intervals = IntervalList(map(lambda b: Interval(b.x, b.x + b.width),
                                 bboxes))
    if len(intervals) == 1:
        return


