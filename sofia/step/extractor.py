from step import Step
from sofia.workflow_template.entity_set import EntitySet


class Extractor(Step):

    PARAMS = ['path']

    def __init__(self, path=[]):
        self.path = path

    def run(self, **kwargs):
        entity = kwargs.values()[0]
        if entity is None:
            return [None]
        return [EntitySet.get_descendent(entity, self.path)]
