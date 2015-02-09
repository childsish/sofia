from action import Action


class Extractor(Action):
    def init(self, path):
        self.path = path

    def calculate(self, **kwargs):
        try:
            entity = kwargs[self.path[0]]
            for step in self.path[1:]:
                entity = entity[step]
            return entity
        except TypeError:
            pass
        return None
