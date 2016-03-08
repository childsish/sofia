from sofia_.step import Target
from sofia_.graph import Workflow
from sofia_.entity import Entity
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
            for resource in resources:
                if resource.alias == 'target' and self.step.matches(resource):
                    return [resource]
            return []
        res = [resource for resource in resources if resource.name != 'target' and self.step.matches(resource)]
        return res

    def _init_step_graph(self, resource):
        """ Create a single node ActionGraph. """
        outs = self.step.get_output({'resource': resource})
        step_instance = self.step({resource}, {}, {}, outs)
        res = Workflow(step_instance)
        res.add_resource(resource)
        return res
