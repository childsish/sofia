from feature import Feature

class Extractor(Feature):
    def init(self, path):
        self.path = path

    def calculate(self, **kwargs):
        entity = kwargs[self.path[0]]
        for step in self.path[1:]:
            entity = entity[step]
        return entity
