from collections import defaultdict

from lhc.graph.hyper_graph import HyperGraph
from ebias.feature_wrapper import FeatureWrapper

class FeatureHyperGraph(object):
    def __init__(self):
        self.outs = defaultdict(list)
        self.features = {}
        self.graph = HyperGraph()
    
    def registerFeature(self, feature, name=None, out=None):
        name = feature.__name__ if name is None else name
        out = feature.OUT if out is None else out
        wrapper = FeatureWrapper(feature, name, out)
        self.feature[name] = wrapper
        self.graph.addVertex(name)
        
        self.graph.addVertex(wrapper.name)
        for out in wrapper.out:
            self.outs[out].append(wrapper.name)
        for in_ in wrapper.in_:
            if in_ not in self.outs:
                self.graph.addEdge(in_, wrapper.name)
            else:
                for child in self.outs[in_]:
                    self.graph.addEdge(in_, wrapper.name, child)
    
    def getFeatureGraph(self, feature, resources):
        if False:
            self.getFeatureGraph(self.graph.getChildren(feature), resources)
