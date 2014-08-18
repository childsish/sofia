from itertools import izip
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
        row = self._getNextRow(requested_features, kwargs)
        while kwargs['target'] is not None:
            yield row
            row = self._getNextRow(requested_features, kwargs)
    
    def _getNextRow(self, requested_features, kwargs):
        for feature in requested_features:
            self.features[feature].reset(self.features)
        self.features['target'].changed = True
        row = []
        for feature in requested_features:
            item = self.features[feature].generate(kwargs, self.features)
            item = '' if item is None else self.features[feature].format(item)
            print 'x:', item
            row.append(item)
        return row

