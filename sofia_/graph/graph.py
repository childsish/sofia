from collections import defaultdict
from uuid import uuid4 as uuid


class Graph(object):
    def __init__(self, name=None):
        self.anon_prefix = str(uuid())[:8]
        self.vertex_id = 0
        self.edge_id = 0

        self.name = 'G' if name is None else name
        self.vs = set()
        self.es = defaultdict(set)
        
    def __str__(self):
        res = ['digraph {} {{'.format(self.name)]
        for v in sorted(self.vs):
            if not v.startswith(self.anon_prefix):
                res.append('    "{}" [label=""]'.format(v))
        for e, vs in sorted(self.es.iteritems()):
            e = '' if e.startswith(self.anon_prefix) else ' [label="{}"]'.format(e)
            for v1, v2 in vs:
                res.append('    "{}" -> "{}"{};'.format(v1, v2, e))
        res.append('}')
        return '\n'.join(res)

    def __len__(self):
        return len(self.vs)
    
    def add_vertex(self, v=None):
        """ Add a vertex to the graph

        :param v: The vertex name. If not given, a unique id will be created.
        :return: The vertex name, given or created.
        """
        if v is None:
            v = '{}.{}'.format(self.anon_prefix, self.vertex_id)
            self.vertex_id += 1
        self.vs.add(v)
        return v
    
    def add_edge(self, v1, v2, e=None):
        """ Add an edge to the graph

        :param v1: The name of the origin vertex.
        :param v2: The name of the destination vertex.
        :param e: The edge name. If not given a unique id will be created.
        :return: The edge name, given or created.
        """
        if e is None:
            e = '{}.{}'.format(self.anon_prefix, self.edge_id)
            self.edge_id += 1
        self.vs.add(v1)
        self.vs.add(v2)
        self.es[e].add((v1, v2))
        return e

    def get_parents(self, v):
        res = set()
        for e, vs in self.es.iteritems():
            for parent, child in vs:
                if v == child:
                    res.add(parent)
        return res
        
    def get_children(self, v):
        res = set()
        for e, vs in self.es.iteritems():
            for parent, child in vs:
                if v == parent:
                    res.add(child)
        return res
