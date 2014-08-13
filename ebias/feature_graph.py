from lhc.graph.graph import Graph

class FeatureGraph(object):
    def __init__(self, feature=None):
        self.feature = feature
        self.features = {}
        self.graph = Graph()
        self.resources = set()
        
        if feature is not None:
            feature_name = feature.getName()
            self.features[feature_name] = feature
            self.graph.addVertex(feature_name)
        
    def __str__(self):
        return str(self.graph)
    
    def addResource(self, resource):
        self.resources.add(resource)
    
    def addEdge(self, edge, fr, to):
        self.graph.addEdge(edge, fr, to)

    def update(self, other):
        self.features.update(other.features)
        self.resources.update(other.resources)
        self.graph.vs.update(other.graph.vs)
        for e in other.graph.es:
            self.graph.es[e].update(other.graph.es[e])

    def iterRows(self, requested_features):
        kwargs = {}
        row = [self.features[feature].generate(kwargs, self.features) for feature in requested_features]
        row = ['' if item is None else self.features[feature].format(item) for item in row]
        while kwargs['target'] is not None:
            yield row
            row = [self.features[feature].generate(kwargs, self.features) for feature in requested_features]
            row = ['' if item is None else self.features[feature].format(item) for item in row]
