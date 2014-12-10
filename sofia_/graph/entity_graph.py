import json

from sofia_.entity import Entity
from graph import Graph

class EntityGraph(object):
    def __init__(self, fname):
        fhndl = open(fname)
        json_obj = json.load(fhndl)
        fhndl.close()

        self.graph = Graph()
        self.attr = {}
        for entity, settings in json_obj.iteritems():
            self.graph.addVertex(entity)
            if 'children' in settings:
                for child in settings['children']:
                    self.graph.addEdge('%s_%s'%(entity, child), entity, child)
            if 'attributes' in settings:
                self.attr[entity] = settings['attributes']

    def getAncestorPaths(self, entity):
        res = []
        stk = [[entity]]
        while len(stk) > 0:
            path = stk.pop()
            for parent in self.graph.getParents(path[-1]):
                stk.append(path + [parent])
                res.append([parent] + path[::-1])
        return res

    def getDescendentPaths(self, entity):
        res = [[entity]]
        stk = [[entity]]
        while len(stk) > 0:
            path = stk.pop()
            if path[-1] in self.graph.vs:
                for edge_name, child in self.graph.getChildren(path[-1]):
                    stk.append(path + [child])
                    res.append(path + [child])
        return res

    def getDescendentPathTo(self, ancestor, descendent):
        paths = self.getDescendentPaths(ancestor)
        for path in paths:
            if path[-1] == descendent:
                return path
        return None

    def createEntity(self, name):
        attr = {}
        for path in [[name]] + self.getDescendentPaths(name):
            for step in path:
                if step not in self.attr:
                    continue
                for name in self.attr[step]:
                    attr[name] = None
        return Entity(name, attr)
