import argparse
import os
import re

from collections import defaultdict
from common import getProgramDirectory
from itertools import izip, product
from modules.resource_parser import ResourceParser
from modules.feature import Feature
from modules.resource import Resource
from modules.parser import Parser
from modules.feature_wrapper import FeatureWrapper
from lhc.graph.graph import Graph
from lhc.graph.hyper_graph import HyperGraph
from lhc.tools import loadPlugins

class Aggregator(object):
    def __init__(self):
        program_dir = getProgramDirectory()
        parsers = loadPlugins(os.path.join(program_dir, 'parsers'), Parser)
        self.resource_parser = ResourceParser({parser.EXT: parser\
            for parser in parsers.itervalues()})

    def aggregate(self, args):
        program_dir = getProgramDirectory()
        
        available_features = loadPlugins(os.path.join(program_dir, 'features'), Feature)
        if 'Resource' in available_features:
            del available_features['Resource']
        wrappers = [FeatureWrapper(feature) for feature in available_features.itervalues()]
        
        requested_features = parseFeatures(args.features)
        #requested_features = [('Chromosome', frozenset()), ('Position', frozenset()), ('GeneName', frozenset(['gtf'])), ('VariantType', frozenset([])), ('CodingVariation', frozenset([])), ('AminoAcidVariation', frozenset(['gtf', 'fasta']))]
        provided_resources = self.resource_parser.parseResources(args.resources)
        provided_resources.append(self.resource_parser.parseTarget(args.input))
        wrappers.extend(provided_resources)
        
        graph = getHyperGraph(wrappers)
        print graph
        resolutions = list(iterGraphPossibilities(requested_features, graph, provided_resources, wrappers))
        if len(resolutions) == 1:
            print resolutions[0]
            resolved_graph, resolved_features = resolutions[0]
            for row in iterRows(requested_features, resolved_features):
                print '\t'.join('' if col is None else resolved_features[feature].format(col) for feature, col in izip(requested_features, row))
        elif len(resolutions) == 0:
            print 'No resolutions were found'
        else:
            print 'Multiple resolutions were found'
            for r in resolutions:
                print r

def main(argv):
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    defineParser(parser)
    return parser

def defineParser(parser):
    parser.add_argument('input', metavar='TARGET',
        help='the file to annotate')
    parser.add_argument('features', nargs='+',
        help='name:[resource[,resource]*]')
    parser.add_argument('-r', '--resources', nargs='+',
        help='name[:type]=fname')
    parser.add_argument('-o', '--output')
    parser.add_argument('-t', '--template')
    parser.add_argument('-y', '--type')
    parser.set_defaults(func=aggregate)

def aggregate(args):
    aggregator = Aggregator()
    aggregator.aggregate(args)

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
    resources = dict((r.name, r) for r in resources)
    feature_graphs = [list(iterFeatureGraphs(requested_feature, graph, set())) for requested_feature, requested_resources in requested_features]
    for cmb in product(*feature_graphs):
        resolved_graph = Graph()
        for (requested_feature, requested_resources), feature_graph in izip(requested_features, cmb):
            labeled_features = labelFeatures(feature_graph, [(r, resources[r].parser.fname) for r in requested_resources])
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
    key = [key for key in features if 'target' in key][0]
    for entity in features[key].parser:
        kwargs[key] = entity
        yield [features[feature].generate(kwargs, features) for feature in requested_features]
        
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

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
