from itertools import izip


class Converter(object):
    def __init__(self, path=None, id_map=None):
        self.path = [] if path is None else [path]
        self.id_map = [] if id_map is None else [id_map]

    def __len__(self):
        return len(self.path)

    def convert(self, entity):
        # TODO: Track number of KeyErrors
        try:
            for path, id_map in izip(self.path, self.id_map):
                tmp = entity
                for step in path[:-1]:
                    tmp = tmp[step]
                tmp[path[-1]] = id_map[tmp[path[-1]]]
            return entity
        except KeyError:
            pass
        return None

    def update(self, other):
        self.path.extend(other.path)
        self.id_map.extend(other.id_map)
