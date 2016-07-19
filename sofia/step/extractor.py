from step import Step
from sofia.workflow_template.entity_set import EntitySet


class Extractor(Step):

    PARAMS = ['path']

    def __init__(self, path=None, **kwargs):
        self.input_stream = kwargs.values()[0].consume()
        self.path = [] if path is None else path

    def run(self, **kwargs):
        entity, output_stream = kwargs.items()[0]
        while len(self.input_stream) > 0:
            res = None if entity is None else EntitySet.get_descendent(self.input_stream.pop(), self.path)
            if not output_stream.push(res):
                break
        if len(self.input_stream) == 0:
            output_stream.push(StopIteration)
