from feature import Feature

from ebias.entity import Entity

class Converter(Feature):
    
    IN = ['id', 'id_map']
    OUT = ['id']
    
    def init(self, path):
        self.path = path

    def calculate(self, id, id_map):
        if len(self.path) == 1:
            return id_map[id]
        res = id.copy()
        entity = res
        for step in self.path[1:-1]:
            entity = entity[step]
        entity[self.path[-1]] = id_map[entity[self.path[-1]]]
        return entity

    @classmethod
    def iterOutput(cls, ins={}, outs={}, attr={}):
        for k in ins:
            if k.endswith('_map'):
                id_map = ins[k]
            else:
                id = ins[k]
        hdrs = id_map.attr['hdrs']
        if id is None or id not in hdrs:
            raise StopIteration()
        for hdr in hdrs:
            yield { out: Entity(out, {out: hdr}) for out in outs }
