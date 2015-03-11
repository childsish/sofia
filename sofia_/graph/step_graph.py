from lhc.graph import Graph


class StepGraph(object):
    """ A resolved graph that calculates a step. """
    def __init__(self, step=None):
        self.step = step
        self.steps = {}
        self.graph = Graph()
        self.resources = set()
        
        if step is not None:
            step_name = step.name
            self.steps[step_name] = step
            self.graph.add_vertex(step_name)
            self.graph.name = type(step).__name__
        
    def __str__(self):
        """ Returns a dot formatted representation of the graph. """
        return str(self.graph)

    def __len__(self):
        return len(self.graph)
    
    def add_resource(self, resource):
        """ Add a resource that this graph depends upon. """
        self.resources.add(resource)
    
    def add_edge(self, edge, fr, to):
        """ Join two steps by a labelled edge. """
        self.graph.add_edge(fr, to, edge)
    
    def init(self):
        """ Initialise all the steps in the graph. """
        for ftr in self.steps.itervalues():
            try:
                ftr.init(**ftr.param)
            except TypeError, e:
                raise TypeError(e.args[0].replace('init()', type(ftr).__name__))

    def update(self, other):
        """ Merge this actionGraph with another. """
        self.steps.update(other.steps)
        self.resources.update(other.resources)
        self.graph.vs.update(other.graph.vs)
        for e in other.graph.es:
            self.graph.es[e].update(other.graph.es[e])
