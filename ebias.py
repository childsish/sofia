import json

from collections import defaultdict
from itertools import izip, product, chain
from modules.encoder import Encoder
from modules.feature import Feature
from modules.resource import Resource, Target
from modules.feature_wrapper import FeatureWrapper
from modules.graph import Graph
from modules.hyper_graph import HyperGraph
from lhc.tools import loadPlugins

def main():
    resource_types = {'vcf': ['variant', 'genomic_position'], 'gtf': ['model']}
    # -r name[:type]=fname
    resources = [('target', None, 'D:\data\tmp.vcf')]
    # -f name:[resource[,resource]*]
    requested_features = [('Chromosome', frozenset()), ('Position', frozenset())]
    
    available_features = loadPlugins('features', Feature)
    del available_features['Resource']
    wrappers = [FeatureWrapper(feature) for feature in available_features.itervalues()]
    for name, type, fname in resources:
        ext = fname.rsplit('.', 1)[1]
        if name == 'target':
            wrappers.append(FeatureWrapper(Target, 'Target', resource_types[ext]))
        else:
            type = [ext] if type is None else type
            wrappers.append(FeatureWrapper(Resource, '%sResource'%ext.capitalize(), type))
    graph = getHyperGraph(wrappers)
    for resolved_graph, resolved_features in iterGraphPossibilities(requested_features, graph, resources, wrappers):
        aggregate(requested_features, resolved_features)

def getHyperGraph(wrappers):
    graph = HyperGraph()
    outs = defaultdict(list)
    for wrapper in wrappers:
        graph.addVertex(wrapper.name)
        for out in wrapper.out:
            outs[out].append(wrapper.name)
    for wrapper in wrappers:
        for in_ in wrapper.in_:
            if in_ not in outs:
                graph.addEdge(in_, wrapper.name)
            else:
                for child in outs[in_]:
                    graph.addEdge(in_, wrapper.name, child)
    return graph

def iterGraphPossibilities(requested_features, graph, resources, wrappers):
    resources = dict((r[0], r) for r in resources)
    feature_graphs = [list(iterFeatureGraphs(requested_feature, graph)) for requested_feature, requested_resources in requested_features]
    for (requested_feature, requested_resources), cmb in izip(requested_features, product(*feature_graphs)):
        resolved_graph = Graph()
        for feature_graph in cmb:
            labeled_features = labelFeatures(feature_graph, [(resource, resources[resource][2]) for resource in requested_resources])
            for v in feature_graph.vs:
                resolved_graph.addVertex((v, frozenset(labeled_features[v])))
            for e, vs in feature_graph.es.iteritems():
                for v1, v2 in vs:
                    resolved_graph.addEdge(e, (v1, frozenset(labeled_features[v1])), (v2, frozenset(labeled_features[v2])))
        available_features = {wrapper.name: wrapper for wrapper in wrappers}
        resolved_features = {feature: available_features[feature[0]].instantiate(dependencies, requested_resources, resources) for feature, dependencies in resolved_graph.vs.iteritems()}
        yield resolved_graph, resolved_features

def iterFeatureGraphs(feature, graph, visited=None):
    if visited is None:
        visited = set()
    if feature != 'Target' and feature in visited:
        raise StopIteration()
    visited.add(feature)
    edge_names = []
    edge_dependencies = []
    for name, dependencies in graph.vs[feature].iteritems():
        edge_names.append(name)
        edge_dependencies.append(list(chain.from_iterable(iterFeatureGraphs(dep, graph, visited) for dep in dependencies)))
    for cmb in product(*edge_dependencies):
        res = Graph()
        res.addVertex(feature)
        keep = True
        for edge, dependee in izip(edge_names, cmb):
            if dependee is None:
                keep = False
                break
            res.addEdge(edge, feature, dependee)
            res.vs.update(dependee.vs)
            res.es.update(dependee.es)
        if keep:
            yield res

def labelFeatures(graph, requested_resources):
    labeled_features = defaultdict(set)
    for name, fname in requested_resources:
        ext = fname.rsplit('.', 1)[1]
        feature = 'Target' if name == 'target' else\
            '%sResource'%ext.capitalize()
        stk = [feature]
        while len(stk) > 0:
            feature = stk.pop()
            labeled_features[feature].add(name)
            stk.extend(graph.getParents(feature))
    return labeled_features

def aggregate(requested_features, features):
    for row in iterRows(requested_features, features):
        print row

def iterRows(requested_features, features):
    kwargs = {}
    for entity in features['Target']:
        kwargs['Target'] = entity
        yield [features[feature].generate(kwargs, features) for feature in requested_features]

if __name__ == '__main__':
    import sys
    sys.exit(main())

#ebias.py $INPUT_VCF aa_mut cai -r 
#ebias.py $INPUT_FASTA aa_mut cai -r target:nucleotide_sequence
