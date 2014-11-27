from itertools import izip

class Converter(object):
    def __init__(self, path=None, id_map=None):
        self.path = [] if path is None else [path]
        self.id_map = [] if id_map is None else [id_map]

    def __len__(self):
        return len(self.path)

    def convert(self, entity):
        it = izip(self.path, self.id_map)
        for path, id_map in it:
            tmp = entity
            for step in path[:-1]:
                tmp = tmp[step]
            tmp[path[-1]] = id_map[tmp[path[-1]]]
        return entity

    def update(self, other):
        self.path.extend(other.path)
        self.id_map.extend(other.id_map)
