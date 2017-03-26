from lhc.graph import Graph


class EntitySet(object):
    def __init__(self):
        self.has_a = Graph()
        self.is_a = Graph()
        self.entities = {}

    def __iter__(self):
        return iter(self.entities.values())

    def __contains__(self, item):
        return item in self.entities

    def register_entity(self, name, description=None, has_a=None, is_a=None, attributes=None):
        if name in self.entities:
            return
        entity = {
            'name': name,
            'description': '' if description is None else description,
            'attributes': set() if attributes is None else set(attributes)
        }
        if has_a is not None:
            entity['has_a'] = has_a
            for to in has_a:
                self.has_a.add_edge(name, to)
        if is_a is not None:
            entity['is_a'] = is_a
            self.is_a.add_edge(is_a, name)
        self.entities[name] = entity

    def is_equivalent(self, a, b):
        return a in self.get_equivalent_descendents(b) or\
            b in self.get_equivalent_descendents(a)

    def get_ancestor_paths(self, entity):
        paths = []
        stk = [[entity]]
        while len(stk) > 0:
            c_path = stk.pop()
            for parent in self.has_a.get_parents(c_path[-1]):
                tmp = c_path + [parent]
                stk.append(tmp)
                paths.append([self.entities[parent_name]['has_a'][child_name]
                              for parent_name, child_name in zip(tmp[:0:-1], tmp[-2::-1])])
        return paths

    def get_descendent_paths(self, entity):
        paths = []
        stk = [[entity]]
        while len(stk) > 0:
            c_path = stk.pop()
            if c_path[-1] not in self.has_a.vs:
                continue
            for child in self.has_a.get_children(c_path[-1]):
                tmp = c_path + [child]
                stk.append(tmp)
                paths.append([self.entities[parent_name]['has_a'][child_name]
                              for parent_name, child_name in zip(tmp[:-1], tmp[1:])])
        return paths

    def get_descendent_path_to(self, ancestor, descendent):
        paths = self.get_descendent_paths(ancestor)
        for path in paths:
            if path[-1]['name'] == descendent:
                return path
        return None

    def get_equivalent_descendents(self, entity):
        if entity in self.is_a:
            return self.is_a.get_descendants(entity)
        return {entity}

    def get_equivalent_ancestors(self, entity):
        if entity in self.is_a:
            return self.is_a.get_ancestors(entity)
        return {entity}

    def update(self, other):
        self.entities.update(other.entities)
        self.has_a.update(other.has_a)
        self.is_a.update(other.is_a)

    @staticmethod
    def get_descendent(entity, path):
        for step in path:
            if step['type'] == 'attr':
                entity = getattr(entity, step['key'])
            elif step['type'] == 'item':
                entity = entity[step['key']]
        return entity
