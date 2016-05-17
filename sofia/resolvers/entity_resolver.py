from sofia.error_manager import ERROR_MANAGER
from sofia.workflow.entity_node import EntityNode


class EntityResolver(object):
    def __init__(self, entity, graph, provided_entities, workflow_template, maps={}, requested_resources=set(), visited=None):
        self.entity = entity
        self.graph = graph
        self.provided_entities = provided_entities
        self.maps = maps
        self.requested_resources = requested_resources
        self.workflow_template = workflow_template

        self.visited = set() if visited is None else visited

    def __str__(self):
        return self.entity
    
    def __iter__(self):
        is_not_provided = True
        for provided_entity in self.provided_entities:
            if provided_entity.name == self.entity:
                is_not_provided = False
                yield EntityNode(provided_entity)

        step_names = self.graph.get_children(self.entity)
        if len(step_names) == 0 and is_not_provided:
            ERROR_MANAGER.add_error('No steps produce {}'.format(self.entity))

        from step_resolver import StepResolver
        for step_name in step_names:
            if step_name in self.visited:
                continue
            step = self.graph.steps[step_name]
            it = StepResolver(step,
                              self.graph,
                              self.provided_entities,
                              self.workflow_template,
                              self.maps,
                              self.requested_resources,
                              set(self.visited))
            for solution in it:
                res = EntityNode(solution.head.outs[self.entity])
                res.add_step_node(solution)
                yield res
