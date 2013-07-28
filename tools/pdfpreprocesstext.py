#!/usr/bin/env python

# standard library imports
from collections import defaultdict
from contextlib import closing
import os.path
import sys

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '..', 'pdfworker')
)

# third party related imports
import ujson

# local library imports
from Rectangle import TextRectangle as TextRect

MIN_DIST = 3.
MIN_RATIO = 0.9
INV_MIN_RATIO = 1 / MIN_RATIO

def naive_merge(a, b):

    r = a | b
    r = TextRect(r.x, r.y, r.w, r.h, '')

    if r.orientation == TextRect.ROW:
        return row_merge(a, b)

    return column_merge(a, b)

def row_merge(a, b):

    r = a | b

    if a.x <= b.x:
        return TextRect(r.x, r.y, r.w, r.h, a.t + b.t)

    return TextRect(r.x, r.y, r.w, r.h, b.t + a.t)

def test_row_merge(orientations, distances, heights):

    global MIN_DIST, MIN_RATIO, INV_MIN_RATIO

    if orientations[0] == TextRect.COL or orientations[1] == TextRect.COL:
        return False

    if distances[1] != 0 or distances[0] > MIN_DIST:
        return False

    r = heights[0] / heights[1]
    if r < MIN_RATIO or r > INV_MIN_RATIO:
        return False

    return True

def column_merge(a, b):

    r = a | b

    if a.y <= b.y:
        return TextRect(r.x, r.y, r.w, r.h, a.t + b.t)

    return TextRect(r.x, r.y, r.w, r.h, b.t + a.t)

def test_column_merge(orientations, distances, widths):

    global MIN_DIST, MIN_RATIO, INV_MIN_RATIO

    if orientations[0] == TextRect.ROW or orientations[1] == TextRect.ROW:
        return False

    if distances[0] != 0 or distances[1] > MIN_DIST:
        return False

    r = widths[0] / widths[1]
    if r < MIN_RATIO or r > INV_MIN_RATIO:
        return False

    return True

def merge(blocks):

    next, curr = [], blocks

    while True:
        num_blocks = len(curr)
        ismerged = [False] * num_blocks

        for i in xrange(num_blocks):
            if ismerged[i]:
                continue

            block1 = curr[i]
            ori1 = block1.orientation

            for j in xrange(i + 1, num_blocks):
                if ismerged[j]:
                    continue

                block2 = curr[j]
                ori2 = block2.orientation

                dx, dy = block1.x_distance(block2), block1.y_distance(block2)

                if ori1 == TextRect.UNKNOWN and ori2 == TextRect.UNKNOWN:
                    may_row_merge = test_row_merge((ori1, ori2), (dx, dy),
                                                   (block1.h, block2.h))
                    may_col_merge = test_column_merge((ori1, ori2), (dx, dy),
                                                      (block1.w, block2.w))
                    if may_row_merge and may_col_merge:
                        block1 = naive_merge(block1, block2)
                        ismerged[j] = True
                        print 'merge', block1.t
                        break
                    elif may_row_merge:
                        block1 = row_merge(block1, block2)
                        ismerged[j] = True
                        print 'merge', block1.t
                        break
                    elif may_col_merge:
                        block1 = column_merge(block1, block2)
                        ismerged[j] = True
                        print 'merge', block1.t
                        break

                if ori1 == TextRect.ROW or ori2 == TextRect.ROW:
                    if test_row_merge((ori1, ori2), (dx, dy),
                                      (block1.h, block2.h)):

                        block1 = row_merge(block1, block2)
                        ismerged[j] = True
                        print 'merge', block1.t
                        break

                if ori1 == TextRect.COL or ori2 == TextRect.COL:
                    if test_column_merge((ori1, ori2), (dx, dy),
                                         (block1.w, block2.w)):

                        block1 = column_merge(block1, block2)
                        ismerged[j] = True
                        print 'merge', block1.t
                        break

            next.append(block1)

        if not any(ismerged):
            break

        curr, next = next, []

    return next

def normalize_coordinate(width, height, blocks, new_width=1000):

    r = new_width / width

    ret_blocks = []
    for block in blocks:
        b = block.copy()
        for attr in ('x', 'y', 'w', 'h'):
            b[attr] = block[attr] * r

        ret_blocks.append(b)

    return new_width, height * r, ret_blocks

def merge_blocks(data):

    width, height, blocks = normalize_coordinate(data['width'], data['height'],
                                                 data['data'])
    blocks = map(lambda b: TextRect(b['x'], b['y'], b['w'], b['h'], b['t']),
                 blocks)
    before_merge = len(blocks)

    blocks = merge(blocks)
    blocks = map(lambda b: {'x': b.x, 'y': b.y, 'w': b.w, 'h': b.h, 't': b.t},
                 blocks)
    after_merge = len(blocks)

    print before_merge, '->', after_merge

    return {'width': width, 'height': height, 'data': blocks}

def main(argv):

    if len(argv) != 2:
        print 'usage: python %s [text-json]' % argv[0]
        exit(1)

    data = None
    with closing(open(argv[1], 'rb')) as f:
        data = ujson.loads(f.read())

    data = merge_blocks(data)

    with closing(open('output.json', 'wb')) as f:
        f.write(ujson.dumps(data, ensure_ascii=False))


if __name__ == '__main__':

    main(sys.argv)
