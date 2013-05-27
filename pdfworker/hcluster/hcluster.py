#!/usr/bin/env python

# standard library imports
from collections import defaultdict

# third party related imports

# local library imports
from Point import Point
from Rectangle import Rectangle


class IAgglomeratable(object):
    """An interface for merging process in hierarchy clustering."""

    def agglomerate(self, closest, **kwargs):
        raise NotImplemented

    def distance_to(self, other, **kwargs):
        raise NotImplemented

    def isleaf(self, **kwargs):
        raise NotImplemented


class TreeNodeStat(object):
    """
    A data structure representing the basic statistics of a TreeNode
    instance.

    Attributes:
        num_char: An integer indicating total number of characters under
            a TreeNode instance.
        avg_font_size: A float indicating average font size under a
            TreeNode instance.
        var_font_size: A float indicating variance of font size under a
            TreeNode instance.

    """

    def __init__(self, num_char=0, font_size=0):

        self.font_size_sample = defaultdict(lambda: 0)
        self.font_size_sample[font_size] = num_char

    @property
    def num_char(self):
        """Number of characters."""

        return sum(self.font_size_sample.values())

    @property
    def avg_font_size(self):
        """Average font size."""

        ret = 0
        num_char = 0
        for font_size in self.font_size_sample:
            ret += font_size * self.font_size_sample[font_size]
            num_char += self.font_size_sample[font_size]

        return 1.0 * ret / num_char if num_char != 0 else 0

    @property
    def var_font_size(self):
        """Font size variance."""

        n = self.num_char

        if n <= 1:
            return 0

        var = 0
        avg = self.avg_font_size
        for font_size in self.font_size_sample:
            d = font_size - avg
            var += self.font_size_sample[font_size] * d * d

        var /= (n - 1)

        return var ** 0.5

    def merge(self, stat):
        """Merge another TreeNodeStat instance."""

        ret = TreeNodeStat()
        ret.font_size_sample = self.font_size_sample.copy()

        for font_size in stat.font_size_sample:
            ret.font_size_sample[font_size] += stat.font_size_sample[font_size]

        return ret


class TreeNode(IAgglomeratable):
    """A node data structure of hierarchy clustering tree.

    Attributes:
        data: Additional data.
        mbr: A minimum bounding rectangle.
        children: A list of TreeNode instances.
        stat: A TreeNodeStat instance.

    """

    def __init__(self, mbr, data=None):

        self.data = data
        self.mbr = mbr
        self.children = []
        self._stat = None

    def agglomerate(self, node, copy_data=False):
        """Merge another TreeNode instance.

        Args:
            node: A TreeNode instance.

        Returns:
            A TreeNode instance.

        """

        ret = TreeNode(self.mbr | node.mbr)
        ret._add_children(self, node)
        if copy_data:
            ret.data = map(lambda c: c.data, ret.children)

        return ret

    def distance_to(self, node):
        """Measure the distance to another TreeNode instance.

        Including the disntance between minimum bounding rectangels and
        average font size.

        Args:
            node: A TreeNode instance.

        Returns:
            A number.

        """

        rect_dist = self.mbr.distance(node.mbr)

        font_size_dist = self.stat.avg_font_size - node.stat.avg_font_size
        font_size_dist *= font_size_dist

        return rect_dist + font_size_dist

    def isleaf(self):
        """Test if it is a leaf node."""

        return len(self.children) == 0

    def _add_children(self, *args):
        """Add TreeNode instances as children nodes.

        Children are added and sorted by their distance to (0, 0).

        """

        self.children.extend(filter(lambda a: isinstance(a, TreeNode), args))
        self.children.sort(key=lambda c: Point(c.mbr.x, c.mbr.y).square_dist())

    def dfs(self):
        """Depth first search"""

        if self.isleaf():
            yield self
        else:
            for c in self.children:
                for node in c.dfs():
                    yield node

    @property
    def stat(self):
        """Get TreeNode statistics."""

        if self._stat is not None:
            return self._stat

        if self.isleaf():
            if isinstance(self.data, basestring):
                self._stat = TreeNodeStat(num_char=len(self.data),
                                          font_size=self.mbr.h)
            else:
                self._stat = TreeNodeStat()

            return self._stat

        self._stat = TreeNodeStat()
        for c in self.children:
            self._stat = self._stat.merge(c.stat)

        return self._stat


def create_dendrogram(leaves, max_num_cluster=1, onmerge=None):
    """Build the hierarchy cluster dendrogram in bottom up manner.

    Args:
        leaves: A list of TreeNode instances. They are treated as
            leaves of the result dendrogram.
        max_num_cluster: A number indicating when to stop the
            merging process.
        onmerge: A callback when merging process is going.

    Returns:
        A list of TreeNode instances its length is `max_num_cluster`.

    """

    if not callable(onmerge):
        onmerge = lambda x, y: 1

    clusters = list(leaves)
    distance_cache = {}

    while len(clusters) > max_num_cluster:
        # construct distance_cache
        min_dist = float('inf')
        closest_nodes = None

        for i, cluster1 in enumerate(clusters):
            for j, cluster2 in enumerate(clusters):
                if i >= j:
                    continue

                cache_key = (cluster1, cluster2)
                if cache_key not in distance_cache:
                    d = cluster1.distance_to(cluster2)
                    distance_cache[cache_key] = d

                d = distance_cache[cache_key]
                if d < min_dist:
                    min_dist = d
                    closest_nodes = (i, j)

        # merge the closest nodes
        merger = clusters[closest_nodes[0]]
        mergee = clusters[closest_nodes[1]]
        new_cluster = merger.agglomerate(mergee)
        clusters[closest_nodes[0]] = new_cluster
        clusters.remove(mergee)

        onmerge(new_cluster, clusters)

        # clear cache
        for key in distance_cache.keys():
            if merger in key or mergee in key:
                del distance_cache[key]

    return clusters
