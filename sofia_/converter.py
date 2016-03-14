from itertools import izip


class Converter(object):
    def __init__(self, entity=None, fr=None, to=None, path=None, id_map=None):
        self.attributes = {} if entity is None else {entity: (fr, to)}
        self.paths = [] if path is None else [path]
        self.id_maps = [] if id_map is None else [id_map]
        self.ttl = 0
        self.cnt = 0

    def __str__(self):
        return ','.join('{}:{}->{}'.format(e, f, t) for e, (f, t) in self.attributes.iteritems())

    def __len__(self):
        return len(self.paths)

    def convert(self, entity):
        self.ttl += 1
        try:
            for path, id_map in izip(self.paths, self.id_maps):
                entity = self._convert(entity, path, id_map)
        except KeyError:
            return None
        self.cnt += 1
        return entity

    def update(self, other):
        self.attributes.update(other.attributes)
        self.paths.extend(other.paths)
        self.id_maps.extend(other.id_maps)

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
