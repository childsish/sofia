from collections import defaultdict

from lhc.graph.hyper_graph import HyperGraph

class FeatureHyperGraph(object):
    def __init__(self):
        self.outs = defaultdict(set)
        self.ins = defaultdict(set)
        self.features = {}
        self.graph = HyperGraph()
    
    def __str__(self):
        return str(self.graph)
    
    def registerFeature(self, feature):
        name = feature.__name__
        self.features[name] = feature
        self.graph.addVertex(name)
        
        for in_ in feature.IN:
            self.ins[in_].add(name)
            self.graph.addEdge(in_, name)
            for child in self.outs[in_]:
                self.graph.addEdge(in_, name, child)
        for out in feature.OUT:
            self.outs[out].add(name)
            for parent in self.ins[out]:
                self.graph.addEdge(out, parent, name)
    
    def getFeatureGraph(self, feature, resources):
        if False:
            self.getFeatureGraph(self.graph.getChildren(feature), resources)
