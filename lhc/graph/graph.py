from collections import defaultdict, namedtuple
from uuid import uuid4 as uuid

Edge = namedtuple('Edge', ('fr', 'to'))
Endpoint = namedtuple('Endpoint', ('edge', 'vertex'))


class Graph(object):

    __slots__ = ('anon_prefix', 'vertex_id', 'edge_id', 'name', 'es', 'vs', 'directed', 'edge_names')

    def __init__(self, es=list(), vs=list(), name=None, directed=True, edge_names='unique'):
        """
        Initialise a graph

        :param es: list of (from, to) pairs of existing edges
        :param vs: list of vertex names (without edges)
        :param name: name of the graph
        :param directed: whether the graph is directed or not (default: True)
        :param edge_names: {'unique', 'vertex'} name edges uniquely or by the sorted fr/to pair
        """
        self.anon_prefix = str(uuid())[:8]
        self.vertex_id = 0
        self.edge_id = 0

        self.name = 'G' if name is None else name
        self.es = {}
        self.vs = defaultdict(set)
        self.directed = directed
        self.edge_names = edge_names

        for fr, to in es:
            self.add_edge(fr, to)
        for v in vs:
            self.add_vertex(v)

    def __str__(self):
        res = ['{} {} {{'.format('digraph' if self.directed else 'graph', self.name)]
        for v in sorted(self.vs):
            if v.startswith(self.anon_prefix):
                res.append('    "{}" [label=""]'.format(v))
        for e, (v1, v2) in sorted(self.es.iteritems()):
            e = '' if e.startswith(self.anon_prefix) else ' [label="{}"]'.format(e)
            res.append('    "{}" -> "{}"{};'.format(v1, v2, e))
        res.append('}')
        return '\n'.join(res)

    def __len__(self):
        return len(self.vs)

    def __delitem__(self, key):
        tos = self.vs[key]
        for to in tos:
            del self.es[(key, to)]
        del self.vs[key]

    def add_edge(self, fr, to, e=None):
        """ Add an edge to the graph

        :param fr: The name of the origin vertex.
        :param to: The name of the destination vertex.
        :param e: The edge name. If not given a unique id will be created.
        :return: The edge name, given or created.
        """
        edge = Edge(fr, to) if self.directed else Edge(min(fr, to), max(fr, to))
        if e is None:
            if self.edge_names == 'unique':
                e = '{}.{}'.format(self.anon_prefix, self.edge_id)
                self.edge_id += 1
            elif self.edge_names == 'vertex':
                e = '{}.{}.{}'.format(self.anon_prefix, edge.fr, edge.to)
        if e in self.es and self.es[e] != edge:
            raise ValueError('edge {} already defined'.format(e))
        self.es[e] = edge
        self.vs[fr].add(Endpoint(edge=e, vertex=to))
        if not self.directed:
            self.vs[to].add(Endpoint(edge=e, vertex=fr))
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

    def decompose(self, removed=None):
        visited = set()
        removed = set() if removed is None else removed
        for fr, tos in self.vs.iteritems():
            if fr in visited or fr in removed:
                continue
            visited.add(fr)
            graph = Graph(vs=[fr], directed=self.directed)
            stk = [(fr, to) for to in tos if to.vertex not in removed]
            for fr, to in stk:
                graph.add_edge(fr, to.vertex, to.edge)
            while len(stk) > 0:
                root, fr = stk.pop()
                if fr.vertex in visited or fr.vertex in removed:
                    continue
                visited.add(fr.vertex)
                es = [(fr.vertex, to) for to in self.vs[fr.vertex] if to.vertex not in removed]
                for fr, to in es:
                    graph.add_edge(fr, to.vertex, to.edge)
                stk.extend(es)
            yield graph

    def update(self, other):
        for e, edge in other.es.iteritems():
            if e in self.es and self.es[e] != edge:
                raise ValueError('edge {} has conflicting endpoints: {}, {}'.format(e, self.es[e], edge))
            elif e.startswith(other.anon_prefix):
                e = self.anon_prefix + e[8:]
            self.es[e] = edge
        self.vs.update(other.vs)
