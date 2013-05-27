#!/usr/bin/env python

# standard library imports

# third party related imports
import pytest

# local library imports
from ..hcluster import TreeNodeStat


class TestTreeNodeStat(object):

    def test_merge(self):

        tns1 = TreeNodeStat(num_char=0, avg_font_size=10)
        tns2 = TreeNodeStat(num_char=0, avg_font_size=100)
        tns3 = tns1.merge(tns2)
        assert(tns3.num_char == 0)
        assert(tns3.avg_font_size == 0)

        tns1 = TreeNodeStat(num_char=1, avg_font_size=10)
        tns2 = TreeNodeStat(num_char=10, avg_font_size=20)
        tns3 = tns1.merge(tns2)
        assert(tns3.num_char == 11)
        assert(tns3.avg_font_size == 1.0 * (1 * 10 + 10 * 20) / 11)
