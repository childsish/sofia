from lhc.graph.graph import Graph

class FeatureGraph(object):
    """ A resolved graph that calculates a feature. """
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
            ftr.init(**ftr.kwargs)

    def update(self, other):
        """ Merge this FeatureGraph with another. """
        self.features.update(other.features)
        self.resources.update(other.resources)
        self.graph.vs.update(other.graph.vs)
        for e in other.graph.es:
            self.graph.es[e].update(other.graph.es[e])

    def iterRows(self, requested_features):
        """ Calculate the features in this graph for each entity in the target
        resource. """
        kwargs = {}
        row = self._getNextRow(requested_features, kwargs)
        while kwargs['target'] is not None:
            yield row
            row = self._getNextRow(requested_features, kwargs)
    
    def _getNextRow(self, requested_features, kwargs):
        """ Return the requested features for the next entity in the target
        resource. """
        for feature in requested_features:
            self.features[feature].reset(self.features)
        self.features['target'].changed = True
        row = []
        for feature in requested_features:
            try:
                item = self.features[feature].generate(kwargs, self.features)
                item = '' if item is None else self.features[feature].format(item)
                row.append(item)
            except Exception, e:
                if isinstance(e, StopIteration):
                    raise e
                import sys
                import traceback
                traceback.print_exception(*sys.exc_info(), file=sys.stderr)
                sys.stderr.write('Error processing entry on line %d\n'%\
                    (self.features['target'].parser.line_no))
                sys.exit(1)
        return row
