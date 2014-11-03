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
    def getOutput(cls, ins={}, outs={}, requested_attr={}):
        for k in ins:
            if k.endswith('_map'):
                id_map_key = k
            else:
                id_key = k
        id_map = ins[id_map_key]
        id = ins[id_key]
        if id_key not in requested_attr or requested_attr[id_key] is None or id.attr[id_key] == requested_attr[id_key]:
            return None
        hdrs = id_map.attr['hdrs']
        if id.attr[id_key] not in hdrs or requested_attr[id_key] not in hdrs:
            ERROR_MANAGER.addError('%s could not find %s "%s" among %s'%\
                (cls.__name__, id_key, id.attr[id_key], ','.join(hdrs)))
            return None
        return { out: Entity(out, requested_attr) for out in outs }
