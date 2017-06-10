from collections import defaultdict
from itertools import product
from operator import or_
from sofia.workflow import StepNodeFactory
from sofia.resolvers.entity_resolver import EntityResolver
from sofia.error_manager import ERROR_MANAGER


class StepResolver(object):
    def __init__(self, step, template, maps=None, requested_resources=set(), visited=None):
        self.step = step
        self.factory = StepNodeFactory(step, [attribute(attribute.ATTRIBUTE, template.entities, step, maps) for attribute in template.attributes.values()])
        self.template = template
        self.maps = maps if maps else {}
        self.requested_resources = requested_resources

        self.visited = set() if visited is None else visited
        self.visited.add(step.name)

    def __str__(self):
        return self.step.name

    def __hash__(self):
        return hash(str(self))
    
    def __iter__(self):
        entities = sorted(self.template.get_parents(self.step.name))
        resolvers = {entity: EntityResolver(entity,
                                            self.template,
                                            maps=self.maps,
                                            requested_resources=self.requested_resources,
                                            visited=self.visited)
                     for entity in entities}
        resolvers = {entity: list(resolver) for entity, resolver in resolvers.items()}

        solutions = defaultdict(list)
        disjoint_solutions = [resolvers[entity] for entity in entities]
        for disjoint_solution in product(*disjoint_solutions):
            try:
                step_node = self.factory.make(disjoint_solution)
            except ValueError as e:
                ERROR_MANAGER.add_error(str(e), self.step.name)
                continue
            resources = set()
            for partial_solution in disjoint_solution:
                resources.update(partial_solution.head.attributes['resource'])
            solutions[len(resources - set(self.requested_resources))].append(step_node)
        if len(solutions) > 0:
            for solution in solutions[min(solutions)]:
                yield solution
