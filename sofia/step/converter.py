from step import Step


class Converter(Step):
    def __init__(self, entity=None, fr=None, to=None, path=None, id_map=None):
        self.attributes = {} if entity is None else {entity: (fr, to)}
        self.path = [] if path is None else path
        self.id_map = [] if id_map is None else id_map
        self.ttl = 0
        self.cnt = 0

    def run(self, **kwargs):
        entity = kwargs[self.outs.keys()[0]]

        self.ttl += 1
        try:
            entity = self._convert(entity, self.path, self.id_map)
        except KeyError:
            entity = None
            self.cnt += 1
        return entity

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
        frq = round(self.cnt / float(self.ttl), 3)
        return {'{}% of identifiers were converted.'.format(frq * 100)} if frq < 1 else {}
