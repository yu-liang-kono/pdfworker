#!/usr/bin/env python

# standard library imports
import argparse
from contextlib import closing
import math
import os.path
import re
import sys

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '..', 'pdfworker')
)
# third party related imports
import ujson
import zhon

# local library imports
from PDFPage import PDFPage
from hcluster.hcluster import create_dendrogram, TreeNode
from hcluster.Rectangle import Rectangle


MIN_COST = float('inf')
NUM_GROUP = 0
OPT_DENDROGRAMS = None


def create_argument_parser():
    """Create augument parser and register parameters."""

    parser = argparse.ArgumentParser(description='Merge texts to paragraphs')
    parser.add_argument(
        '--group',
        type=int,
        help=('Set number of groups. '
              'If not set, groups will be decided automatically')
    )
    parser.add_argument('page-json')

    return parser


def create_treenode(page_data):
    """
    Given a basic text block in page data, create a TreeNode instance
    to represent it.

    """

    rect = Rectangle(page_data['x'], page_data['y'],
                     page_data['w'], page_data['h'])
    return TreeNode(rect, data=page_data['t'])


def onmerge(new_cluster, clusters):
    """Callback function."""

    global MIN_COST, NUM_GROUP, OPT_DENDROGRAMS

    num_clusters = len(clusters)
    if not 3 <= num_clusters <= 50:
        return

    num_cluster_cost = 1. / (1. + math.exp(-0.1 * num_clusters))
    font_size_cost = sum(map(lambda c: c.stat.var_font_size / c.stat.avg_font_size, clusters))
    cost = num_cluster_cost + font_size_cost

    if cost < MIN_COST:
        MIN_COST = cost
        NUM_GROUP = num_clusters
        OPT_DENDROGRAMS = map(lambda c: c.clone(), clusters)

    #print 'num_cluster(', num_clusters, '):', num_cluster_cost, \
    #      'font_size:', font_size_cost, \
    #      'cost:', num_cluster_cost + font_size_cost


def replace_space(match_obj):

    test_string = match_obj.string
    strlen = len(test_string)
    if match_obj.end() < strlen:
        next_char = match_obj.string[match_obj.end()]
        if re.match('[%s|%s]' % (zhon.unicode.HAN_IDEOGRAPHS,
                                 zhon.unicode.PUNCTUATION),
                    next_char):
            return ''

    return match_obj.group(0)


def main():

    arg_parser = create_argument_parser()
    arg_dict = vars(arg_parser.parse_args())

    # open page json
    with closing(open(arg_dict['page-json'], 'rb')) as f:
        page = PDFPage.create_by_json(f.read())

    leaf_nodes = map(create_treenode, page.data)
    if len(leaf_nodes) < 2:
        return map(lambda n: n.data, leaf_nodes)

    max_num_cluster = arg_dict.get('group', 0)
    if max_num_cluster > 0:
        dendrograms = create_dendrogram(leaf_nodes,
                                        max_num_cluster=max_num_cluster)
    else:
        create_dendrogram(leaf_nodes, max_num_cluster=1, onmerge=onmerge)
        dendrograms = OPT_DENDROGRAMS

    nodes = map(lambda (ix, ddgram): TreeNode(ddgram.mbr, data=ix),
                enumerate(dendrograms))
    root = create_dendrogram(nodes, max_num_cluster=1)[0]
    paragraphs = []
    for cluster in root.dfs():
        ix = cluster.data
        paragraph = u''.join((node.data for node in dendrograms[ix].dfs()))
        paragraph = paragraph.strip()
        paragraph = re.sub('(?<=[%s|%s])\s+' % (zhon.unicode.HAN_IDEOGRAPHS,
                                                zhon.unicode.PUNCTUATION),
                           replace_space,
                           paragraph)
        paragraphs.append(paragraph)

    print ujson.dumps(paragraphs, ensure_ascii=False)


if __name__ == "__main__":

    main()
