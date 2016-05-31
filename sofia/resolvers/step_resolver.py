from collections import defaultdict
from itertools import product
from operator import or_
from sofia.workflow import StepNodeFactory
from entity_resolver import EntityResolver
from sofia.error_manager import ERROR_MANAGER


class StepResolver(object):
    def __init__(self, step, template, provided_entities, maps={}, requested_entities=set(), visited=None):
        self.step = step
        self.factory = StepNodeFactory(step, [attribute(attribute.ATTRIBUTE, template.entity_graph, step, maps) for attribute in template.attributes])
        self.template = template
        self.provided_entities = provided_entities
        self.maps = maps
        self.requested_entities = requested_entities

        self.visited = set() if visited is None else visited
        self.visited.add(step.name)

    def __str__(self):
        return self.step.name

    def __hash__(self):
        return hash(str(self))
    
    def __iter__(self):
        entities = sorted(self.template.get_children(self.step.name))
        resolvers = {entity: EntityResolver(entity,
                                            self.template,
                                            self.provided_entities,
                                            self.maps,
                                            self.requested_entities,
                                            self.visited)
                     for entity in entities}
        resolvers = {entity: list(resolver) for entity, resolver in resolvers.iteritems()}

        res = defaultdict(list)
        disjoint_solutions = [resolvers[entity] for entity in entities]
        for disjoint_solution in product(*disjoint_solutions):
            try:
                step_node = self.factory.make(disjoint_solution)
            except ValueError, e:
                ERROR_MANAGER.add_error(e.message, self.step.name)
                continue
            resources = reduce(or_, (partial_solution.head.attributes['resource'] for partial_solution in disjoint_solution), set())
            res[len(resources - set(self.requested_entities))].append(step_node)
        if len(res) > 0:
            for solution in res[min(res)]:
                yield solution
