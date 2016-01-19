from step import Step
from resource import Resource


class Map(Resource):

    OUT = ['map']
    FORMAT = 'map'

    def init(self):
        resource = list(self.resources)[0]
        attr = resource.attr
        in_cols = [int(col) - 1 for col in attr['in_cols'].split(',')]
        out_cols = [int(col) - 1 for col in attr['out_cols'].split(',')]
        fhndl = open(resource.fname)
        fhndl.readline()
        lines = [line.rstrip('\r\n').split('\t') for line in fhndl]
        self.parser = {tuple(parts[col] for col in in_cols): parts[out_cols[0]] for parts in lines}\
            if len(out_cols) == 1 else\
            {tuple(parts[col] for col in in_cols): tuple(parts[col] for col in out_cols) for parts in lines}
        fhndl.close()


class GetIdById(Step):

    IN = ['id', 'map']
    OUT = ['id']

    def calculate(self, id, map):
        return map.get((id,), None)
