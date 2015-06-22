class EntityWrapper(object):
    def __init__(self, entity, path, id_map):
        self.entity = entity
        self.path = path
        self.id_map = id_map

    def __getitem__(self, key):
        value = self.entity[key]
        if self.path[0]['type'] == 'item' and key == self.path[0]['key']:
            if len(self.path) == 1:
                return self.id_map[self.value]
            return EntityWrapper(value, self.path[1:], self.id_map)
        return value

    def __getattr__(self, key):
        value = getattr(self.entity, key)
        if self.path[0]['type'] == 'attr' and key == self.path[0]['key']:
            if len(self.path) == 1:
                return self.id_map[value]
            return EntityWrapper(value, self.path[1:], self.id_map)
        return value
