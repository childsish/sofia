import json

from sofia_.entity import Entity
from lhc.graph import Graph


class EntityGraph(object):
    def __init__(self, fname):
        fhndl = open(fname)
        json_obj = json.load(fhndl)
        fhndl.close()

        self.graph = Graph()
        self.attr = {}
        for entity, settings in json_obj.iteritems():
            self.graph.add_vertex(entity)
            if 'children' in settings:
                for child in settings['children']:
                    self.graph.add_edge(entity, child, '{}_{}'.format(entity, child))
            if 'attributes' in settings:
                self.attr[entity] = settings['attributes']

    def get_ancestor_paths(self, entity):
        res = []
        stk = [[entity]]
        while len(stk) > 0:
            path = stk.pop()
            for parent in self.graph.get_parents(path[-1]):
                stk.append(path + [parent])
                res.append([parent] + path[::-1])
        return res

    def get_descendent_paths(self, entity):
        res = [[entity]]
        stk = [[entity]]
        while len(stk) > 0:
            path = stk.pop()
            if path[-1] in self.graph.vs:
                for child in self.graph.get_children(path[-1]):
                    stk.append(path + [child])
                    res.append(path + [child])
        return res

    def get_descendent_path_to(self, ancestor, descendent):
        paths = self.get_descendent_paths(ancestor)
        for path in paths:
            if path[-1] == descendent:
                return path
        return None

    def create_entity(self, name):
        attr = {}
        for path in [[name]] + self.get_descendent_paths(name):
            for step in path:
                if step not in self.attr:
                    continue
                for name in self.attr[step]:
                    attr[name] = None
        return Entity(name, attr)

    @classmethod
    def get_entity_name(cls, entity):
        return ''.join(part.capitalize() for part in entity.split('_')).replace('*', '')
