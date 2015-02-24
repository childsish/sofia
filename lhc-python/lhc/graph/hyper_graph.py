from graph import Graph


class HyperGraph(object):
    def __init__(self, name=None):
        self.name = 'G' if name is None else name
        self.graph = Graph()
        self.vs = set()
        self.es = set()
    
    def __str__(self):
        """ Convert to string

        :return: A string representing the graph in Graphviz format.
        """
        res = ['digraph {} {{'.format(self.name)]
        for e in sorted(self.es):
            res.append('    {} [shape=box];'.format(e))
        for e, vs in sorted(self.graph.es.iteritems()):
            for v in vs:
                res.append('    "{}" -> "{}";'.format(*v))
        res.append('}')
        return '\n'.join(res)
    
    def add_vertex(self, v):
        """ Add a vertex to the graph

        :param v: The vertex name.
        """
        self.graph.add_vertex(v)
        self.vs.add(v)

    def add_outward_edge(self, v, e):
        """ Add an outward edge to a vertex

        :param v: The source vertex.
        :param e: The name of the outward edge.
        """
        self.add_vertex(v)
        self.graph.add_vertex(e)
        self.es.add(e)
        self.graph.add_edge(e, v)

    def add_inward_edge(self, v, e):
        """ Add an inward edge to a vertex

        :param v: The destination vertex.
        :param e: The name of the inward edge.
        """
        self.add_vertex(v)
        self.graph.add_vertex(e)
        self.es.add(e)
        self.graph.add_edge(v, e)

    def get_parents(self, n):
        """ Get the parents of a vertex or edge.

        :param n: A vertex or edge.
        :return: The children of the given vertex or edge.
        """
        return self.graph.get_parents(n)

    def get_children(self, n):
        """ Get the children of a vertex or edge.

        :param n: A vertex or edge.
        :return: The children of the given vertex or edge.
        """
        return self.graph.get_children(n)
