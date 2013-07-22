#!/usr/bin/env

# standard library imports

# third party related imports

# local library imports
from ..hcluster import TreeNode, create_dendrogram, Rectangle


class TestTreeNode(object):

    def test_agglomerate(self):

        node1 = TreeNode(Rectangle(0, 0, 10, 10), '1')
        node2 = TreeNode(Rectangle(10, 10, 10, 10), '2')
        node3 = node1.agglomerate(node2)

        assert(node3.mbr == Rectangle(0, 0, 20, 20))
        assert(len(node3.children) == 2)
        assert(node3.children[0] == node1)
        assert(node3.children[1] == node2)


        node1 = TreeNode(Rectangle(100, 100, 10, 5), '1')
        node2 = TreeNode(Rectangle(50, 50, 55, 55), '2')
        node3 = node1.agglomerate(node2, copy_data=True)

        assert(node3.mbr == Rectangle(50, 50, 60, 55))
        assert(len(node3.children) == 2)
        assert(node3.children[0] == node2)
        assert(node3.children[1] == node1)
        assert(node3.data == ['2', '1'])

    def test_distance(self):

        node1 = TreeNode(Rectangle(0, 0, 10, 10), '1')
        node2 = TreeNode(Rectangle(100, 100, 10, 10), '2')
        assert(node1.distance_to(node2) == 16200 + 0)

        node1 = TreeNode(Rectangle(0, 0, 10, 10), 'abcd')
        node2 = TreeNode(Rectangle(1, 1, 9, 9), 'ef')
        assert(node1.distance_to(node2) == 0 + 1)

    def test_isleaf(self):

        node1 = TreeNode(Rectangle(0, 0, 1, 1))
        node2 = TreeNode(Rectangle(1, 1, 1, 1))
        node3 = node1.agglomerate(node2)

        assert(node1.isleaf())
        assert(node2.isleaf())
        assert(not node3.isleaf())

    def test_dfs(self):

        NUM_NODES = 5
        nodes = [TreeNode(Rectangle(i, i, 1, 1), str(i)) for i in xrange(NUM_NODES)]

        for node in nodes:
            for visitee in node.dfs():
                assert(visitee == node)

        node = nodes[0]
        for i in xrange(1, NUM_NODES):
            node = node.agglomerate(nodes[i])

        for ix, visitee in enumerate(node.dfs()):
            assert(visitee.data == str(ix))

    def test_stat(self):

        node1 = TreeNode(Rectangle(0, 0, 2, 2), 'abc')
        node2 = TreeNode(Rectangle(0, 0, 10, 10), 'def')
        assert(node1.stat.num_char == 3)
        assert(node1.stat.avg_font_size == 2)
        assert(node1.stat.var_font_size == 0)
        assert(node2.stat.num_char == 3)
        assert(node2.stat.avg_font_size == 10)
        assert(node2.stat.var_font_size == 0)

        node3 = node1.agglomerate(node2)
        assert(node3.stat.num_char == 3 + 3)
        assert(node3.stat.avg_font_size == 1.0 * (2 * 3 + 10 * 3) / (3 + 3))
        expected_var = 3 * 2 * 2 + 3 * 10 * 10 - 6 * node3.stat.avg_font_size ** 2
        expected_var /= (6 - 1)
        expected_var **= 0.5
        assert(node3.stat.var_font_size - expected_var < 1.0e-6)

    def test_create_dendrogram(self):

        nodes = (
            TreeNode(Rectangle(0, 0, 1, 1), '0'),
            TreeNode(Rectangle(2, 2, 1, 1), '1'),
            TreeNode(Rectangle(4, 4, 1, 1), '2'),
            TreeNode(Rectangle(6, 6, 1, 1), '3'),
        )

        dendrograms = create_dendrogram(nodes, max_num_cluster=3)
        assert(dendrograms[0].mbr == nodes[0].agglomerate(nodes[1]).mbr)
        assert(dendrograms[1].mbr == nodes[2].mbr)
        assert(dendrograms[2].mbr == nodes[3].mbr)

        dendrograms = create_dendrogram(nodes, max_num_cluster=2)
        assert(dendrograms[0].mbr == \
               nodes[0].agglomerate(nodes[1]).agglomerate(nodes[2]).mbr)
        assert(dendrograms[1].mbr == nodes[3].mbr)

        dendrograms = create_dendrogram(nodes, max_num_cluster=1)
        assert(dendrograms[0].mbr == \
               Rectangle(0, 0, 7, 7))
