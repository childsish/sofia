from lhc.graph.graph import Graph

class FeatureGraph(object):
    """ A resolved graph that calculates a feature. """
    def __init__(self, feature=None):
        self.feature = feature
        self.features = {}
        self.graph = Graph()
        self.resources = set()
        
        if feature is not None:
            feature_name = feature.name
            self.features[feature_name] = feature
            self.graph.addVertex(feature_name)
            self.graph.name = type(feature).__name__
        
    def __str__(self):
        """ Returns a dot formatted representation of the graph. """
        return str(self.graph)
    
    def addResource(self, resource):
        """ Add a resource that this graph depends upon. """
        self.resources.add(resource)
    
    def addEdge(self, edge, fr, to):
        """ Join two features by a labelled edge. """
        self.graph.addEdge(edge, fr, to)
    
    def init(self):
        """ Initialise all the features in the graph. """
        for ftr in self.features.itervalues():
            try:
                ftr.init(**ftr.param)
            except TypeError, e:
                raise TypeError(e.args[0].replace('init()', type(ftr).__name__))

    def update(self, other):
        """ Merge this FeatureGraph with another. """
        self.features.update(other.features)
        self.resources.update(other.resources)
        self.graph.vs.update(other.graph.vs)
        for e in other.graph.es:
            self.graph.es[e].update(other.graph.es[e])
