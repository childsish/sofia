from lhc.graph.graph import Graph


class ActionGraph(object):
    """ A resolved graph that calculates a action. """
    def __init__(self, action=None):
        self.action = action
        self.actions = {}
        self.graph = Graph()
        self.resources = set()
        
        if action is not None:
            action_name = action.name
            self.actions[action_name] = action
            self.graph.addVertex(action_name)
            self.graph.name = type(action).__name__
        
    def __str__(self):
        """ Returns a dot formatted representation of the graph. """
        return str(self.graph)
    
    def addResource(self, resource):
        """ Add a resource that this graph depends upon. """
        self.resources.add(resource)
    
    def addEdge(self, edge, fr, to):
        """ Join two steps by a labelled edge. """
        self.graph.addEdge(edge, fr, to)
    
    def init(self):
        """ Initialise all the steps in the graph. """
        for ftr in self.actions.itervalues():
            try:
                ftr.init(**ftr.param)
            except TypeError, e:
                raise TypeError(e.args[0].replace('init()', type(ftr).__name__))

    def update(self, other):
        """ Merge this actionGraph with another. """
        self.actions.update(other.actions)
        self.resources.update(other.resources)
        self.graph.vs.update(other.graph.vs)
        for e in other.graph.es:
            self.graph.es[e].update(other.graph.es[e])
