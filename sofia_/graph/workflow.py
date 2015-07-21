from lhc.graph import Graph


class Workflow(object):
    """ A resolved graph that calculates a step. """
    def __init__(self, step=None):
        self.step = step
        self.steps = {}
        self.graph = Graph(directed=True)
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
    
    def init(self):
        """ Initialise all the steps in the graph. """
        #TODO: Check if param is still necessary
        for ftr in self.steps.itervalues():
            ftr.init(**ftr.param)

    def join(self, edge, fr, to, other):
        """ Merge this StepGraph with another. """
        self.graph.update(other.graph)
        self.steps.update(other.steps)
        self.resources.update(other.resources)
        self.graph.add_edge(edge, fr, to)
