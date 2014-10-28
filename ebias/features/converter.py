from feature import Feature

from ebias.entity import Entity
from ebias.error_manager import ERROR_MANAGER

class Converter(Feature):
    
    IN = ['id', 'id_map']
    OUT = ['id']
    
    def init(self, path, map):
        self.path = path
        self.map = map

    def calculate(self, **kwargs):
        id_map = kwargs[self.map]
        fr = self.ins[self.path[0]].attr[self.path[-1]]
        to = self.outs[self.path[0]].attr[self.path[-1]]
        res = kwargs[self.path[0]].copy()
        if len(self.path) == 1:
            return id_map.mapIdentifier(fr, to, res)
        entity = res
        for step in self.path[1:-1]:
            entity = entity[step]
        entity[self.path[-1]] = id_map.mapIdentifier(fr, to, entity[self.path[-1]])
        return res
    
    @classmethod
    def iterOutput(cls, ins={}, outs={}, attr={}):
        for k in cls.IN:
            if not k.endswith('_map'):
                id_key = k
        for k in ins:
            if k.endswith('_map'):
                id_map = ins[k]
            else:
                id = ins[k]
        hdrs = id_map.attr['hdrs']
        if id.attr[id_key] not in hdrs:
            ERROR_MANAGER.addError('%s could not find %s %s in %s'%\
                (cls.__name__, id_key, id, ','.join(hdrs)))
            raise StopIteration()
        for hdr in hdrs:
            attr = id.attr.copy()
            attr[id_key] = hdr
            yield { out: Entity(out, attr) for out in outs }
