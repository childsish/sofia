__author__ = 'Liam Childs'

import unittest

from lhc.graph import Graph


class TestGraph(unittest.TestCase):
    def test_init_noarg(self):
        graph = Graph()

        self.assertEquals(0, graph.edge_id)
        self.assertEquals(0, graph.vertex_id)
        self.assertEquals('G', graph.name)
        self.assertEquals(0, len(graph.es))
        self.assertEquals(0, len(graph.vs))

    def test_init_arg(self):
        graph = Graph([('a', 'b'), ('a', 'c'), ('b', 'd'), ('d', 'a')])

        self.assertEquals(4, graph.edge_id)
        self.assertEquals(0, graph.vertex_id)
        self.assertEquals('G', graph.name)
        self.assertEquals(4, len(graph.es))
        self.assertEquals(4, len(graph.vs))

    def test_unnamed_vertices(self):
        graph = Graph()
        v1 = graph.add_vertex()
        v2 = graph.add_vertex()
        e = graph.add_edge(v1, v2)

        self.assertEquals(1, graph.edge_id)
        self.assertEquals(2, graph.vertex_id)
        self.assertEquals('G', graph.name)
        self.assertEquals(1, len(graph.es))
        self.assertEquals(2, len(graph.vs))
        self.assertEquals((v1, v2), graph.es[e])

    def test_get_family(self):
        graph = Graph([('a', 'b'), ('a', 'c'), ('b', 'd'), ('d', 'a')])

        self.assertEquals({'b', 'c'}, graph.get_children('a'))
        self.assertEquals({'b'}, graph.get_parents('d'))

    def test_decompose(self):
        graph = Graph()
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
