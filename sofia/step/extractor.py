from sofia.graph import EntityGraph
from step import Step


class Extractor(Step):

    PARAMS = ['path']

    def init(self, path=[]):
        self.path = path

    def calculate(self, **kwargs):
        entity = kwargs[list(self.ins)[0]]
        if entity is None:
            return None
        return EntityGraph.get_descendent(entity, self.path)
