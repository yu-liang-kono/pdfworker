#!/usr/bin/env python

# standard library imports
from contextlib import closing
import math
import os.path
import sys

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '..', 'pdfworker')
)
# third party related imports

# local library imports
from PDFPage import PDFPage
from hcluster.hcluster import create_dendrogram, TreeNode
from hcluster.Rectangle import Rectangle


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

    num_clusters = len(clusters)
    if not 3 <= num_clusters <= 50:
        return

    num_cluster_cost = 1. / (1. + math.exp(-0.1 * num_clusters))

    font_size_cost = sum(map(lambda c: c.stat.var_font_size / c.stat.avg_font_size, clusters))
    print 'num_cluster(', num_clusters, '):', num_cluster_cost, \
          'font_size:', font_size_cost, \
          'cost:', num_cluster_cost + font_size_cost


def main(argv):

    with closing(open(argv[1], 'rb')) as f:
        page = PDFPage.create_by_json(f.read())

    leaf_nodes = map(create_treenode, page.data)
    dendrograms = create_dendrogram(leaf_nodes, max_num_cluster=int(argv[2]),
                                    onmerge=onmerge)
    nodes = map(lambda (ix, ddgram): TreeNode(ddgram.mbr, data=ix),
                enumerate(dendrograms))

    root = create_dendrogram(nodes, max_num_cluster=1)[0]
    for cluster in root.dfs():
        ix = cluster.data
        print ''.join([node.data for node in dendrograms[ix].dfs()])
        print '----------------------'


if __name__ == "__main__":

    main(sys.argv)
