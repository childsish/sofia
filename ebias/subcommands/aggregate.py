import argparse
import os
import re
import json

from collections import defaultdict, Counter
from common import getProgramDirectory, loadFeatureHyperGraph
from itertools import izip, chain, product
from ebias.feature_parser import FeatureParser
from ebias.resource_parser import ResourceParser
from ebias.feature_graph import FeatureGraph

class Aggregator(object):
    def __init__(self):
        self.hyper_graph = loadFeatureHyperGraph()

    def aggregate(self, requested_features, provided_resources):
        resolutions = list(self.iterGraphPossibilities(requested_features, provided_resources))
        if len(resolutions) == 1:
            resolution, resolved_features = resolutions[0]
            hdrs = []
            for feature, resources, kwargs in requested_features:
                hdr = [feature]
                if len(resources) > 0:
                    hdr.append(','.join(resources))
                if len(kwargs) > 0:
                    hdr.append(','.join('%s=%s'%e for e in kwargs.iteritems()))
                hdrs.append(':'.join(hdr))
            print '\t'.join(hdrs)
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
        feature_graphs = [[graph for graph in iterGraphs(requested_feature, provided_resources, set(), kwargs) if satisfiesRequest(graph, requested_resources)]\
            for requested_feature, requested_resources, kwargs in requested_features]
        
        missing_features = [requested_feature for feature_graph, (requested_feature, requested_resources, kwargs) in izip(feature_graphs, requested_features) if len(feature_graph) == 0]
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
        help='request a feature using the following format <name>[:<arguments>][:<resources>]', default=[])
    parser.add_argument('-f', '--feature',
        help='specify a feature file in json format')
    parser.add_argument('-o', '--output',
        help='direct output to named file (stdout)')
    parser.add_argument('-r', '--resources', nargs='+',
        help='provide a resource using the following format <file name>[;<type>][;<name>]')
    parser.add_argument('-t', '--template',
        help='specify a template string for the output')
    parser.add_argument('-y', '--type',
        help='specify the type of entity in the target file')
    #parser.add_argument('-g', '--graph', action='StoreTrue')
    parser.set_defaults(func=aggregate)

def aggregate(args):
    feature_parser = FeatureParser()
    requested_features = [feature_parser.parse(ftr) for ftr in args.features]
    provided_resources = parseProvidedResources(args.input, args.resources)
    aggregator = Aggregator()
    aggregator.aggregate(requested_features, provided_resources)
        
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
