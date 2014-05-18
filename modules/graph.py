from collections import defaultdict

class Graph(object):
    def __init__(self):
        self.vs = {}
        self.es = defaultdict(set)
    
    def addVertex(self, v):
        if v not in self.vs:
            self.vs[v] = {}
    
    def addEdge(self, e, v1, v2=None):
        self.vs[v1][e] = v2
        self.es[e].add((v1, v2))

    def getParents(self, v):
        res = set()
        for parent, edges in self.vs.iteritems():
            if v in edges.values():
                res.add(parent)
        return res
        
    def getChildren(self, v):
        return self.vs[v].items()
