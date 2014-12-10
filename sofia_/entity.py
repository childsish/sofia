class Entity(object):
    def __init__(self, name, attr=None):
        self.name = name
        self.attr = {} if attr is None else attr

    def __str__(self):
        return self.name