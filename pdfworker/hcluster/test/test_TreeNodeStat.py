#!/usr/bin/env python

# standard library imports

# third party related imports
import pytest

# local library imports
from ..hcluster import TreeNodeStat


class TestTreeNodeStat(object):

    def test_merge(self):

        tns1 = TreeNodeStat(num_char=0, font_size=10)
        tns2 = TreeNodeStat(num_char=0, font_size=100)
        tns3 = tns1.merge(tns2)
        assert(tns3.num_char == 0)
        assert(tns3.avg_font_size == 0)
        assert(tns3.var_font_size == 0)

        tns1 = TreeNodeStat(num_char=1, font_size=10)
        tns2 = TreeNodeStat(num_char=10, font_size=20)
        tns3 = tns1.merge(tns2)
        assert(tns3.num_char == 11)
        assert(tns3.avg_font_size == 1.0 * (1 * 10 + 10 * 20) / 11)
        expected_var = (tns3.avg_font_size - 10) ** 2
        expected_var += 10 * (tns3.avg_font_size - 20) ** 2
        expected_var /= (11 - 1)
        assert(expected_var ** 0.5 - tns3.var_font_size < 1.0e-6)
