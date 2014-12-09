from collections import defaultdict

class HyperGraph(object):
    def __init__(self, name=None):
        self.name = 'G' if name is None else name
        self.vs = {}
        self.es = defaultdict(set)
    
    def __str__(self):
        res = ['digraph %s {'%self.name]
        for e in self.es:
            res.append('    %s [shape=box];'%e)
        edges = set()
        for v1, es in self.vs.iteritems():
            for e, v2s in es.iteritems():
                edges.add((v1, e))
                for v2 in v2s:
                    edges.add((e, v2))
        res.extend('    %s -> %s;'%edge for edge in edges)
        res.append('}')
        return '\n'.join(res)
    
    def addVertex(self, v):
        if v not in self.vs:
            self.vs[v] = defaultdict(set)
    
    def addEdge(self, e, v1, v2=None):
        if v2 is None:
            self.vs[v1][e] = set()
            self.es[e] = set()
        else:
            self.vs[v1][e].add(v2)
            self.es[e].add((v1, v2))
