import argparse
import json
import pprint
import re

from collections import defaultdict
from itertools import izip, product, chain
from modules.encoder import Encoder
from modules.parser import Parser
from modules.feature import Feature
from modules.resource import Resource, Target
from modules.feature_wrapper import FeatureWrapper
from modules.resource_wrapper import ResourceWrapper, TargetWrapper
from lhc.graph.graph import Graph
from lhc.graph.hyper_graph import HyperGraph
from lhc.tools import loadPlugins

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    aggregate_parser = subparsers.add_parser('aggregate')
    aggregate_parser.add_argument('input')
    aggregate_parser.add_argument('features', nargs='+',
        help='name:[resource[,resource]*]')
    aggregate_parser.add_argument('-r', '--resources', nargs='+',
        help='name[:type]=fname')
    aggregate_parser.add_argument('-o', '--output')
    aggregate_parser.add_argument('-t', '--template')
    aggregate_parser.set_defaults(func=aggregate)
    
    return parser

def aggregate(args):
    parsers = loadPlugins('parsers', Parser)
    for parser in parsers.itervalues():
        Resource.registerParser(parser)
    
    available_features = loadPlugins('features', Feature)
    if 'Feature' in available_features:
        del available_features['Feature']
    if 'Resource' in available_features:
        del available_features['Resource']
    wrappers = [FeatureWrapper(feature) for feature in available_features.itervalues()]
    
    resource_types = {'vcf': ['variant', 'genomic_position'], 'gtf': ['model']}
    #requested_features = parseFeatures(args.features)
    requested_features = [('Chromosome', frozenset()), ('Position', frozenset()), ('GeneName', frozenset(['gtf'])), ('GenePosition', frozenset(['gtf'])), ('AminoAcidMutation', frozenset(['gtf', 'fasta']))]
    #provided_resources = parseResources(args.resources)
    provided_resources = [('target', None, r'D:\data\tmp.KRAS.vcf'), ('gtf', None, r'D:\data\tmp.KRAS.gtf'), ('fasta', None, r'D:\data\tmp.fasta')]
    
    for name, out, fname in provided_resources:
        ext = fname.rsplit('.', 1)[-1]
        wrappers.append(TargetWrapper(fname, resource_types[ext]) if name == 'target' else\
                        ResourceWrapper(fname, out))
    graph = getHyperGraph(wrappers)
    resolutions = list(iterGraphPossibilities(requested_features, graph, provided_resources, wrappers))
    if len(resolutions) == 1:
        resolved_graph, resolved_features = resolutions[0]
        for row in iterRows(requested_features, resolved_features):
            print '\t'.join(resolved_features[feature].format(col) for feature, col in izip(requested_features, row))
    else:
        print 'Multiple resolutions were found'
    

def parseFeatures(features):
    """ -f name[:resource[,resource]*] """
    regx = re.compile('(?P<name>\w+)(?P<resources>[\w,:]+)?')
    res = []
    for feature in features:
        match = regx.match(feature)
        name = match.group('name')
        resources = frozenset() if match.group('resources') is None\
            else frozenset(match.group('resources').split(','))
        res.append((name, resources))
    return res

def parseResources(resources):
    """ -r name[:type]=fname """
    regx = re.compile('(?P<name>\w+)(?::(?P<type>\w+))?=(?P<fname>.+)')
    res = []
    for resource in resources:
        match = regx.match(resource)
        res.append(match.groups())
    return res

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
    feature_graphs = [list(iterFeatureGraphs(requested_feature, graph, set())) for requested_feature, requested_resources in requested_features]
    for cmb in product(*feature_graphs):
        resolved_graph = Graph()
        for (requested_feature, requested_resources), feature_graph in izip(requested_features, cmb):
            labeled_features = labelFeatures(feature_graph, [(resource, resources[resource][2]) for resource in requested_resources])
            for v in feature_graph.vs:
                resolved_graph.addVertex((v, frozenset(labeled_features[v])))
            for e, vs in feature_graph.es.iteritems():
                for v1, v2 in vs:
                    resolved_graph.addEdge(e, (v1, frozenset(labeled_features[v1])), (v2, frozenset(labeled_features[v2])))
        available_features = {wrapper.name: wrapper for wrapper in wrappers}
        resolved_features = {name: available_features[name[0]].instantiate(name, dependencies, requested_resources, resources) for name, dependencies in resolved_graph.vs.iteritems()}
        yield resolved_graph, resolved_features

def iterFeatureGraphs(feature, graph, visited):
    if feature != 'Target' and feature in visited:
        raise StopIteration()
    visited.add(feature)
    for e, v2s in graph.vs[feature].iteritems():
        if len(v2s) == 0:
            print 'broken:', feature, e
    edge_names = sorted(graph.vs[feature].iterkeys())
    edge_dependencies = [iterDependencies(graph.vs[feature][edge], graph, set(visited)) for edge in edge_names]
    for cmb in product(*edge_dependencies):
        res = Graph()
        res.addVertex(feature)
        for edge, (dependee, dependee_graph) in izip(edge_names, cmb):
            res.addEdge(edge, feature, dependee)
            res.vs.update(dependee_graph.vs)
            for e in dependee_graph.es:
                res.es[e].update(dependee_graph.es[e])
        yield res

def iterDependencies(dependencies, graph, visited):
    # Each edge may have several dependencies and each dependency may have several resolutions
    for dependency in dependencies:
        for dependency_graph in iterFeatureGraphs(dependency, graph, visited):
            yield (dependency, dependency_graph)

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

def iterRows(requested_features, features):
    kwargs = {}
    key = [key for key in features if 'Target' in key][0]
    for entity in features[key]:
        kwargs[key] = entity
        yield [features[feature].generate(kwargs, features) for feature in requested_features]

if __name__ == '__main__':
    import sys
    sys.exit(main())
