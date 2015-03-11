from sofia_.step import Resource
from sofia_.error_manager import ERROR_MANAGER


class EntitySolutionIterator(object):
    def __init__(self, entity, graph, provided_resources, workflow_template, maps={}, requested_resources=set(), visited=None):
        self.entity = entity
        self.graph = graph
        self.provided_resources = provided_resources
        self.maps = maps
        self.requested_resources = requested_resources
        self.workflow_template = workflow_template

        self.visited = set() if visited is None else visited

    def __str__(self):
        return self.entity
    
    def __iter__(self):
        step_names = self.graph.get_children(self.entity)
        if len(step_names) == 0:
            ERROR_MANAGER.add_error('No steps produce {}'.format(self.entity))
        for step_name in step_names:
            if step_name in self.visited:
                continue
            step = self.graph.steps[step_name]
            if issubclass(step.step_class, Resource):
                from resource_solution_iterator import ResourceSolutionIterator
                it = ResourceSolutionIterator(step, self.provided_resources, self.workflow_template)
            else:
                from step_solution_iterator import StepSolutionIterator
                it = StepSolutionIterator(step,
                                          self.graph,
                                          self.provided_resources,
                                          self.workflow_template,
                                          self.maps,
                                          self.requested_resources,
                                          set(self.visited))
            for solution in it:
                yield solution
