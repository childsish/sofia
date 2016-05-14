from step import Step
from sofia.graph.entity_graph import EntityGraph


class Extractor(Step):

    PARAMS = ['path']

    def init(self, path=[]):
        self.path = path

    def run(self, **kwargs):
        entity = kwargs[list(self.ins)[0]]
        if entity is None:
            return [None]
        return [EntityGraph.get_descendent(entity, self.path)]
