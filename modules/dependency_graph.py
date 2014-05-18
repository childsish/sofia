from itertools import product
from operator import or_

class HyperGraph(object):
    def addNode(self, node):
        self.nodes[node.name] = node.edges
        for edge in node.edges:
            self.edges[edge]

class DependencyGraph(object):
    def __init__(self):
        self.features = {}
        self.outs = {}
        self.ins = {}
    
    def addFeature(self, feature):
        self.features[feature.name] = feature
        for out in feature.out:
            if out not in self.outs:
                self.outs[out] = []
            self.outs[out].append(feature.name)
        for in_ in feature.in_:
            if in_ not in self.ins:
                self.ins[in_] = []
            self.ins[in_].append(feature.name)
    
    def resolve(self, requested_outputs, given_resources):
        for out, requested_resources in requested_outputs:
            for feature in self.outs[out]:
                print self.resolveFeature(self.features[feature], requested_resources, given_resources, [])
    
    def resolveFeature(self, feature, requested_resources, resources, visited):
        if feature.name in visited:
            return None
        visited.append(feature.name)
        
        cmbs = list(product(*[self.outs[in_] for in_ in feature.in_]))
        for cmb in cmbs:
            dependees = [self.resolveFeature(self.features[dependee], requested_resources, resources, visited[:]) for dependee in cmb]
            if None in dependees:
                continue
            concrete_feature = feature.instantiate(requested_resources, resources)
            extra_resources = reduce(or_, (dependee[1] for dependee in dependees), set())
            concrete_feature.addResources(extra_resources)
            graph = {concrete_feature.getName(): concrete_feature}
            for dependee in dependees:
                graph.update(dependee[0])
            return graph, concrete_feature.resources
