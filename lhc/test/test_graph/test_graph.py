__author__ = 'Liam Childs'

import unittest

from lhc.graph import Graph


class TestGraph(unittest.TestCase):

    def test_init_arg(self):
        graph = Graph([('a', 'b'), ('a', 'c'), ('b', 'd'), ('d', 'a')], directed=False)

        self.assertEquals(4, graph.edge_id)
        self.assertEquals(0, graph.vertex_id)
        self.assertEquals('G', graph.name)
        self.assertEquals(4, len(graph.es))
        self.assertEquals(4, len(graph.vs))

    def test_get_family(self):
        graph = Graph([('a', 'b'), ('a', 'c'), ('b', 'd'), ('d', 'a')], directed=False)

        self.assertEquals({'b', 'c', 'd'}, graph.get_children('a'))

    def test_decompose(self):
        graph = Graph(directed=False)
        graph.add_edge('a', 'b', 'ab')
        graph.add_edge('a', 'c', 'ac')
        graph.add_edge('b', 'd', 'bd')
        graph.add_edge('d', 'a', 'da')
        graph.add_edge('e', 'f', 'ef')
        graph.add_edge('e', 'g', 'eg')

        graphs = graph.decompose()
        graph1, graph2 = (graphs[0], graphs[1]) if 'a' in graphs[0].vs else (graphs[1], graphs[0])

        self.assertEquals({'ab', 'ac', 'bd', 'da'}, set(graph1.es))
        self.assertEquals({'a', 'b', 'c', 'd'}, set(graph1.vs))
        self.assertEquals({'ef', 'eg'}, set(graph2.es))
        self.assertEquals({'e', 'f', 'g'}, set(graph2.vs))


if __name__ == '__main__':
    unittest.main()
