from collections import Counter
from copy import copy
from sofia.step.step import Step
from lhc.order import natural_key
from lhc.binf.genomic_coordinate.genomic_position import ChromosomeIdentifier


class Converter(Step):
    def __init__(self, map_file, fr, to, path=None, order=None):
        self.map = self.load_map_file(map_file, fr, to,
                                      lambda x: ChromosomeIdentifier(tuple(natural_key(x))) if order == 'natural' else lambda x: x)
        self.path = [] if path is None else path
        self.ttl = 0
        self.cnt = Counter()

    def run(self, **kwargs):
        entities = copy(next(iter(kwargs.values())))
        for entity in entities:
            if entity is not None:
                self.ttl += 1
                try:
                    entity = self._convert(entity, self.path, self.map)
                except KeyError as e:
                    self.cnt[str(e)] += 1
                    entity = None
            yield entity
        del next(iter(kwargs.values()))[:]

    def _convert(self, entity, path, id_map):
        if len(path) == 0:
            return id_map[entity]

        step = path[0]
        child = getattr(entity, step['key']) if step['type'] == 'attr' else\
            getattr(entity, step['key'])() if step['type'] == 'function' else\
            entity[step['key']]
        value = self._convert(child, path[1:], id_map)

        if step['type'] == 'attr':
            if hasattr(entity, '_replace'):  # for tuples
                entity = entity._replace(**{path[0]['key']: value})
            else:
                entity = copy(entity)
                setattr(entity, step['key'], value)
        elif step['type'] == 'function':
            entity = copy(entity)
            getattr(entity, step['key'])(value)
        else:
            entity = entity.copy()
            entity[step['key']] = value

        return entity

    def get_user_warnings(self):
        frqs = {msg: round(cnt / float(self.ttl), 3) for msg, cnt in self.cnt.items()}
        return {'{}% of conversions produced error {}'.format(frq * 100, msg) for msg, frq in frqs.items()}

    def load_map_file(self, filename, fr, to, key):
        with open(filename) as fileobj:
            hdrs = fileobj.readline().strip().split('\t')
            fr_idx = hdrs.index(fr)
            to_idx = hdrs.index(to)
            map = {key(parts[fr_idx].strip()): key(parts[to_idx].strip()) for parts in (line.split('\t') for line in fileobj)}
        return map
