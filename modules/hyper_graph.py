from collections import defaultdict

class HyperGraph(object):
    def __init__(self):
        self.vs = {}
        self.es = defaultdict(set)
    
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
