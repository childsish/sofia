from sofia.step.step import Step
from sofia.workflow_template.entity_set import EntitySet


class Extractor(Step):

    PARAMS = ['path']

    def __init__(self, path=None):
        self.path = [] if path is None else path

    def run(self, **kwargs):
        entities = next(iter(kwargs.values()))
        for entity in entities:
            res = None if entity is None else EntitySet.get_descendent(entity, self.path)
            yield res
        del entities[:]
