import json

from sofia_.entity import Entity
from lhc.graph import Graph


class EntityGraph(object):
    def __init__(self, fname):
        fhndl = open(fname)
        entities = json.load(fhndl)
        fhndl.close()

        self.entities = {entity['name']: entity for entity in entities}
        for entity in self.entities.itervalues():
            entity['has_a'] = {child['name']: child for child in entity.get('has_a', [])}

        self.has_a = Graph()
        self.is_a = Graph()
        self.attr = {}
        for entity in self.entities.itervalues():
            self.has_a.add_vertex(entity['name'])
            for child in entity.get('has_a', []):
                self.has_a.add_edge(entity['name'], child)
            if 'is_a' in entity:
                self.is_a.add_edge(entity['is_a'], entity['name'])
            if 'attributes' in entity:
                self.attr[entity['name']] = entity['attributes']

    def __contains__(self, item):
        return item in self.entities

    def register_entity(self, name, description=None, has_a=None, is_a=None):
        if name in self.entities:
            return
        entity = {'name': name}
        if description is not None:
            entity['description'] = description
        if has_a is not None:
            entity['has_a'] = has_a
        if is_a is not None:
            entity['is_a'] = is_a
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
        equivalents = {entity}
        children = self.is_a.get_children(entity)
        while len(children) > 0:
            entity = list(children)[0]
            equivalents.add(entity)
            children = self.is_a.get_children(entity)
        return equivalents

    def get_equivalent_ancestors(self, entity):
        equivalents = {entity}
        parents = self.is_a.get_parents(entity)
        while len(parents) > 0:
            entity = list(parents)[0]
            equivalents.add(entity)
            parents = self.is_a.get_parents(entity)
        return equivalents

    def create_entity(self, name):
        attr = {attr: None for attr in self.attr.get(name, [])}
        for path in self.get_descendent_paths(name):
            for step in path:
                if step['name'] not in self.attr:
                    continue
                for name in self.attr[step['name']]:
                    attr[name] = None
        return Entity(name, attr=attr)

    @classmethod
    def get_entity_name(cls, entity):
        return ''.join(part.capitalize() for part in entity.split('_')).replace('*', '')

    @staticmethod
    def get_descendent(entity, path):
        for step in path:
            if step['type'] == 'attr':
                entity = getattr(entity, step['key'])
            elif step['type'] == 'item':
                entity = entity[step['key']]
        return entity
