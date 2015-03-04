from action import Action
from sofia_.graph.entity_graph import EntityGraph


class Extractor(Action):
    def init(self, path):
        self.path = path

    def calculate(self, **kwargs):
        entity = kwargs[list(self.ins)[0]]
        if entity is None:
            return None
        return EntityGraph.get_descendent(entity, self.path)
