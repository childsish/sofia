from itertools import izip
from sofia_.entity_wrapper import EntityWrapper


class Converter(object):
    def __init__(self, entity=None, fr=None, to=None, path=None, id_map=None):
        self.entities = {} if entity is None else {entity: (fr, to)}
        self.paths = [] if path is None else [path]
        self.id_maps = [] if id_map is None else [id_map]

    def __str__(self):
        return ','.join('{}:{}->{}'.format(e, f, t) for e, (f, t) in self.entities.iteritems())

    def __len__(self):
        return len(self.paths)

    def convert(self, entity):
        # TODO: Track number of KeyErrors
        try:
            for path, id_map in izip(self.paths, self.id_maps):
                entity = self._convert(entity, path, id_map)
        except KeyError:
            return None
        return entity

    def update(self, other):
        self.entities.update(other.entities)
        self.paths.extend(other.paths)
        self.id_maps.extend(other.id_maps)

    def _convert(self, entity, path, id_map):
        if len(path) == 0:
            return id_map[entity]

        child = getattr(entity, path[0]['key']) if path[0]['type'] == 'attr' else\
            entity[path[0]['key']]
        value = self._convert(child, path[1:], id_map)
        if hasattr(entity, '__setitem__'):
            entity = entity.copy()
            entity[path[0]['key']] = value
        elif hasattr(entity, '_replace'):
            entity = entity._replace(**{path[0]['key']: value})
        else:
            entity = EntityWrapper(entity, path, id_map)
        return entity
