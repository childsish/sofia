from collections import Counter
from step import Step
from copy import copy


class Converter(Step):
    def __init__(self, map_file, fr, to, path=None):
        self.map = self.load_map_file(map_file, fr, to)
        self.path = [] if path is None else path
        self.ttl = 0
        self.cnt = Counter()

    def run(self, **kwargs):
        entity = copy(kwargs.values()[0])
        if entity is None:
            yield None
            raise StopIteration()

        self.ttl += 1
        try:
            entity = self._convert(entity, self.path, self.map)
        except KeyError, e:
            self.cnt[e.message] += 1
            entity = None
        yield entity

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
                setattr(entity, step['key'], value)
        elif step['type'] == 'function':
            getattr(entity, step['key'])(value)
        else:
            entity = entity.copy()
            entity[step['key']] = value

        return entity

    def get_user_warnings(self):
        frqs = {msg: round(cnt / float(self.ttl), 3) for msg, cnt in self.cnt.iteritems()}
        return {'{}% of conversions produced error {}'.format(frq * 100, msg) for msg, frq in frqs.iteritems()}

    def load_map_file(self, filename, fr, to):
        with open(filename) as fileobj:
            hdrs = fileobj.readline().strip().split('\t')
            fr_idx = hdrs.index(fr)
            to_idx = hdrs.index(to)
            map = {parts[fr_idx].strip(): parts[to_idx].strip() for parts in (line.split('\t') for line in fileobj)}
        return map
