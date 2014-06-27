from collections import defaultdict

from lhc.graph.hyper_graph import HyperGraph

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
        
        outs = defaultdict(list)
        for wrapper in wrappers:
            graph.addVertex(wrapper.name)
            for out in wrapper.out:
                outs[out].append(wrapper.name)
        for wrapper in wrappers:
            for in_ in wrapper.in_:
                if in_ not in outs:
                    graph.addEdge(in_, wrapper.name)
                else:
                    for child in outs[in_]:
                        graph.addEdge(in_, wrapper.name, child)
        return graph
    
    def getFeatureGraph(self, feature, resources):
        if False:
            self.getFeatureGraph(self.graph.getChildren(feature), resources)
