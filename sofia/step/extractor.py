from step import Step, EndOfStream
from sofia.workflow_template.entity_set import EntitySet


class Extractor(Step):

    PARAMS = ['path']

    def __init__(self, in_, out, path=None):
        self.in_ = in_
        self.out = out
        self.path = [] if path is None else path

    def __str__(self):
        return 'get {} from {}'.format(self.out, self.in_)

    def run(self, ins, outs):
        input_stream = getattr(ins, self.in_)
        output_stream = getattr(outs, self.out)
        while len(input_stream) > 0:
            entity = input_stream.pop()
            if entity is EndOfStream:
                output_stream.push(EndOfStream)
                return True

            res = None if entity is None else EntitySet.get_descendent(entity, self.path)
            if not output_stream.push(res):
                break
        return len(ins) == 0
