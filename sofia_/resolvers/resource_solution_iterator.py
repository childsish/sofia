from sofia_.action import Target
from sofia_.graph.action_graph import ActionGraph
from sofia_.parser.provided_resource import ProvidedResource
from sofia_.error_manager import ERROR_MANAGER


class ResourceSolutionIterator(object):
    def __init__(self, action, resources):
        self.action = action
        self.c_hit = 0
        self.hits = self._get_hits(resources)

    def __str__(self):
        return self.action.name

    def __iter__(self):
        if len(self.hits) == 0:
            ERROR_MANAGER.addError('%s does not match any provided resource' %
                                   self.action.name)
        for hit in self.hits:
            yield self._init_action_graph(hit)

    def _get_hits(self, resources):
        action = self.action.action_class
        if issubclass(action, Target) and action.matches(resources['target']):
            return [resources['target']]
        res = [resource for resource in resources.itervalues()
               if resource.name != 'target' and action.matches(resource)]
        if hasattr(action, 'DEFAULT'):
            import os
            import sys

            fname = action.DEFAULT
            full_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'data', fname)
            res.append(ProvidedResource(full_path, action.OUT[0]))
        return res

    def _init_action_graph(self, resource):
        """ Create a single node ActionGraph. """
        outs = self.action.getOutput({'resource': resource})
        action_instance = self.action({resource}, {}, {}, outs)
        res = ActionGraph(action_instance)
        res.add_resource(resource)
        return res