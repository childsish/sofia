import json

from collections import defaultdict
from modules.encoder import Encoder
from modules.feature import Feature
from modules.resource import Resource, Target
from modules.feature_wrapper import FeatureWrapper
from modules.graph import Graph
from modules.hyper_graph import HyperGraph
from modules.dependency_graph import DependencyGraph
from lhc.tools import loadPlugins

def main():
    resource_types = {'vcf': ['variant', 'genomic_position'], 'gtf': ['model']}
    # -r name[:type]=fname
    resources = [('target', None, 'tmp.vcf'), ('1000genomes', None, '1000genomes.vcf'), ('6200exomes', None, '6200exomes.vcf')]
    # -f match_vcf:1000genomes match_vcf:6200exomes
    requested_features = [('MatchVcf', frozenset(['1000genomes'])), ('MatchVcf', frozenset(['6200exomes']))]
    
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
    resolved_graph = Graph()
    resources = dict((r[0], r) for r in resources)
    for feature, requested_resources in requested_features:
        feature_graph = getFeatureGraph(feature, graph)
        labeled_features = labelFeatures(feature_graph, [(resource, resources[resource][2]) for resource in requested_resources])
        for v in feature_graph.vs:
            resolved_graph.addVertex((v, frozenset(labeled_features[v])))
        for e, vs in feature_graph.es.iteritems():
            for v1, v2 in vs:
                resolved_graph.addEdge(e, (v1, frozenset(labeled_features[v1])), (v2, frozenset(labeled_features[v2])))
    aggregate(resolved_graph, requested_features)

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

def getFeatureGraph(feature, graph, visited=None):
    if visited is None:
        visited = set()
    if feature in visited:
        return
    visited.add(feature)
    res = Graph()
    res.addVertex(feature)
    for edge, dependees in graph.vs[feature].iteritems():
        for dependee in dependees:
            dependencies = getFeatureGraph(dependee, graph, visited)
            if dependencies is not None:
                res.addEdge(edge, feature, dependee)
                res.vs.update(dependencies.vs)
                res.es.update(dependencies.es)
                break
        if dependencies is None:
            return
    return res

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

def aggregate(graph, features):
    for row in iterRows(graph, features):
        print row

def iterRows(graph, features):
    kwargs = {}
    for entity in features['target']:
        kwargs['target'] = entity
        yield [resolveFeature(graph, feature, kwargs) for feature in features]

def resolveFeature(graph, feature):
    kwargs = {edge: resolveFeature(dependee) for edge, dependee in graph.vs[feature]}
    return all_features[feature].calculate(**kwargs)

if __name__ == '__main__':
    import sys
    sys.exit(main())

#ebias.py $INPUT_VCF aa_mut cai -r 
#ebias.py $INPUT_FASTA aa_mut cai -r target:nucleotide_sequence
