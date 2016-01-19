from lhc.graph import Graph


class Workflow(object):
    """ A resolved graph that calculates a step. """
    def __init__(self, step=None):
        self.step = step
        self.steps = {}
        self.graph = Graph(directed=True, edge_names='vertex')
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
        for step in self.steps.itervalues():
            # TODO: Currently only initialise resources
            params = {key: step.attr[key] for key in step.PARAMS if key in step.attr}
            step.init(**params)

    def join(self, other, edge=None):
        """ Merge this workflow with another. """
        self.graph.update(other.graph)
        self.steps.update(other.steps)
        self.resources.update(other.resources)
        if edge is not None:
            self.graph.add_edge(self.step.name, other.step.name)
