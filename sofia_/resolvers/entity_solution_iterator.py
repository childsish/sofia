from sofia_.action import Resource
from sofia_.error_manager import ERROR_MANAGER


class EntitySolutionIterator(object):
    def __init__(self, entity, graph, provided_resources, maps={}, requested_resources=set(), visited=None):
        self.entity = entity
        self.graph = graph
        self.provided_resources = provided_resources
        self.maps = maps
        self.requested_resources = requested_resources

        self.visited = set() if visited is None else visited

    def __str__(self):
        return self.entity
    
    def __iter__(self):
        action_names = self.graph.get_children(self.entity)
        if len(action_names) == 0:
            ERROR_MANAGER.addError('No actions produce {}'.format(self.entity))
        for action_name in self.graph.get_children(self.entity):
            if action_name in self.visited:
                continue
            action = self.graph.actions[action_name]
            if issubclass(action.action_class, Resource):
                from resource_solution_iterator import ResourceSolutionIterator
                it = ResourceSolutionIterator(action, self.provided_resources)
            else:
                from action_solution_iterator import ActionSolutionIterator
                it = ActionSolutionIterator(action,
                                            self.graph,
                                            self.provided_resources,
                                            self.maps,
                                            self.requested_resources,
                                            set(self.visited))
            for solution in it:
                yield solution
