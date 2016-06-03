from step import Step
from sofia.workflow_template.entity_set import EntitySet


class Extractor(Step):

    PARAMS = ['path']

    def __init__(self, path=None):
        self.path = [] if path is None else path

    def run(self, **kwargs):
        entity = kwargs.values()[0]
        if entity is None:
            yield None
        yield EntitySet.get_descendent(entity, self.path)
