import argparse
import os
import re
import json

from collections import defaultdict, Counter
from common import getProgramDirectory, loadFeatureHyperGraph
from itertools import izip, chain, product
from ebias.resource_parser import ResourceParser
from ebias.feature_graph import FeatureGraph

class Aggregator(object):
    def __init__(self):
        self.hyper_graph = loadFeatureHyperGraph()

    def aggregate(self, requested_features, provided_resources):
        resolutions = list(self.iterGraphPossibilities(requested_features, provided_resources))
        if len(resolutions) == 1:
            resolution, resolved_features = resolutions[0]
            print '\t'.join(feature[0] for feature in requested_features)
            for row in resolution.iterRows(resolved_features):
                print '\t'.join(row)
        elif len(resolutions) == 0:
            print 'No resolutions were found'
        else:
            print 'Multiple resolutions were found'
            for r in resolutions:
                print r[0]

    def iterGraphPossibilities(self, requested_features, provided_resources):
        def satisfiesRequest(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources
        
        iterGraphs = self.hyper_graph.iterFeatureGraphs
        feature_graphs = [[graph for graph in iterGraphs(requested_feature, provided_resources, set()) if satisfiesRequest(graph, requested_resources)]\
            for requested_feature, requested_resources in requested_features]
        
        missing_features = [requested_feature for feature_graph, (requested_feature, requested_resources) in izip(feature_graphs, requested_features) if len(feature_graph) == 0]
        if len(missing_features) > 0:
            raise ValueError('Unable to resolve a graph for requested feature: %s'%','.join(missing_features))
        
        for cmb in product(*feature_graphs):
            combined_graph = FeatureGraph()
            resolved_features = []
            for feature_graph in cmb:
                combined_graph.update(feature_graph)
                resolved_features.append(feature_graph.feature.getName())
            yield combined_graph, resolved_features

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
        help='name[:type]=fname', default=[])
    parser.add_argument('-o', '--output')
    parser.add_argument('-t', '--template')
    parser.add_argument('-y', '--type')
    #parser.add_argument('-g', '--graph', action='StoreTrue')
    parser.set_defaults(func=aggregate)

def aggregate(args):
    requested_features = parseRequestedFeatures(args.features)
    provided_resources = parseProvidedResources(args.input, args.resources)
    aggregator = Aggregator()
    aggregator.aggregate(requested_features, provided_resources)
        
def parseRequestedFeatures(features):
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

def parseProvidedResources(target, resources):
    program_dir = getProgramDirectory()
    fhndl = open(os.path.join(program_dir, 'config.json'))
    config = json.load(fhndl)
    fhndl.close()
    default_types = {type['ext']: type['type'] for type in config['default_types']}
    resource_parser = ResourceParser(default_types)
    provided_resources = resource_parser.parseResources(resources)
    provided_resources['target'] = resource_parser.createResource(target, name='target')
    return provided_resources

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
