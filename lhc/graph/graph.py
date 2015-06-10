from collections import defaultdict, namedtuple
from uuid import uuid4 as uuid

Edge = namedtuple('Edge', ('name', 'vertex'))


class Graph(object):
    def __init__(self, es=list(), vs=list(), name=None, directed=True):
        """
        Initialise a graph

        :param es: list of (from, to) pairs of existing edges
        :param vs: list of vertex names (without edges)
        :param name: name of the graph
        :param directed: whether the graph is directed or not (default: True)
        """
        self.anon_prefix = str(uuid())[:8]
        self.vertex_id = 0
        self.edge_id = 0

        self.name = 'G' if name is None else name
        self.es = {}
        self.vs = defaultdict(set)
        self.directed = directed
        for fr, to in es:
            self.add_edge(fr, to)
        for v in vs:
            self.add_vertex(v)

    def __str__(self):
        res = ['{} {} {{'.format('digraph' if self.directed else 'graph', self.name)]
        for v in sorted(self.vs):
            if v.startswith(self.anon_prefix):
                res.append('    "{}" [label=""]'.format(v))
        for e, vs in sorted(self.es.iteritems()):
            e = '' if e.startswith(self.anon_prefix) else ' [label="{}"]'.format(e)
            for v1, v2 in vs:
                res.append('    "{}" -> "{}"{};'.format(v1, v2, e))
        res.append('}')
        return '\n'.join(res)

    def __len__(self):
        return len(self.vs)

    def add_edge(self, fr, to, e=None):
        """ Add an edge to the graph

        :param fr: The name of the origin vertex.
        :param to: The name of the destination vertex.
        :param e: The edge name. If not given a unique id will be created.
        :return: The edge name, given or created.
        """
        if e is None:
            e = '{}.{}'.format(self.anon_prefix, self.edge_id)
            self.edge_id += 1
        self.es[e] = (fr, to)
        self.vs[fr].add(Edge(name=e, vertex=to))
        if not self.directed:
            self.vs[to].add(Edge(name=e, vertex=fr))
        elif to not in self.vs:
            self.vs[to] = set()
        return e
    
    def add_vertex(self, v=None):
        """ Add a vertex to the graph

        :param v: The vertex name. If not given, a unique id will be created.
        :return: The vertex name, given or created.
        """
        if v is None:
            v = '{}.{}'.format(self.anon_prefix, self.vertex_id)
            self.vertex_id += 1
        if v not in self.vs:
            self.vs[v] = set()
        return v

    def get_parents(self, v):
        res = set()
        for e, (parent, child) in self.es.iteritems():
            if v == child:
                res.add(parent)
        return res
        
    def get_children(self, v):
        return {edge.vertex for edge in self.vs[v]}

    def decompose(self, visited=None):
        graphs = []
        visited = set() if visited is None else visited
        for fr, tos in self.vs.iteritems():
            if fr in visited:
                continue
            visited.add(fr)
            stk = [(fr, to) for to in tos]
            graph = Graph(vs=[fr])
            for fr, to in stk:
                graph.add_edge(fr, to.vertex, to.name)
            while len(stk) > 0:
                root, fr = stk.pop()
                if fr.vertex in visited:
                    continue
                visited.add(fr.vertex)
                es = [(fr.vertex, to) for to in self.vs[fr.vertex]]
                for fr, to in es:
                    graph.add_edge(fr, to.vertex, to.name)
                stk.extend(es)
            graphs.append(graph)
        return graphs
