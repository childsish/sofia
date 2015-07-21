from sofia_.step import Target
from sofia_.graph import Workflow
from sofia_.parser.provided_resource import ProvidedResource
from sofia_.error_manager import ERROR_MANAGER


class ResourceSolutionIterator(object):
    def __init__(self, step, resources, workflow_template):
        self.step = step
        self.c_hit = 0
        self.workflow_template = workflow_template
        self.hits = self._get_hits(resources)

    def __str__(self):
        return self.step.name

    def __iter__(self):
        if len(self.hits) == 0:
            ERROR_MANAGER.add_error('{} does not match any provided resource'.format(self.step.name))
        for hit in self.hits:
            yield self._init_step_graph(hit)

    def _get_hits(self, resources):
        step = self.step.step_class
        if issubclass(step, Target):
            return [resources['target']] if self.step.matches(resources['target']) else []
        res = [resource for resource in resources.itervalues()
               if resource.name != 'target' and self.step.matches(resource)]
        if hasattr(step, 'DEFAULT'):
            import os
            import sys

            fname = step.DEFAULT
            full_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'templates',
                                     self.workflow_template, 'data', fname)
            res.append(ProvidedResource(full_path, step.OUT[0]))
        return res

    def _init_step_graph(self, resource):
        """ Create a single node ActionGraph. """
        outs = self.step.get_output({'resource': resource})
        step_instance = self.step({resource}, {}, {}, outs)
        res = Workflow(step_instance)
        res.add_resource(resource)
        return res
