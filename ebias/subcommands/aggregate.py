import argparse
import json
import os
import sys

from common import getProgramDirectory, loadFeatureHyperGraph
from itertools import izip, product
from ebias.feature_parser import FeatureParser
from ebias.resource_parser import ResourceParser
from ebias.feature_graph import FeatureGraph
from ebias.requested_feature import RequestedFeature
from ebias.provided_resource import ProvidedResource

class Aggregator(object):
    def __init__(self):
        self.hyper_graph = loadFeatureHyperGraph()

    def aggregate(self, requested_features, provided_resources, args):
        sys.stderr.write('    Resolving graphs...\n\n')
        
        resolutions = list(self.iterGraphPossibilities(requested_features, provided_resources))
        if len(resolutions) == 1 and not args.graph:
            resolution, resolved_features = resolutions[0]
            resolution.init()
            print '\t'.join([str(ftr) for ftr in requested_features])
            for row in resolution.iterRows(resolved_features):
                print '\t'.join(row)
        elif len(resolutions) == 0:
            sys.stderr.write('    No resolutions were found.\n\n')
        else:
            if len(resolutions) > 1:
                sys.stderr.write('    Multiple resolutions were found.\n\n')
            for r in resolutions:
                sys.stderr.write('%s\n\n'%r[0])

    def iterGraphPossibilities(self, requested_features, provided_resources):
        def satisfiesRequest(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources
        
        iterGraphs = self.hyper_graph.iterFeatureGraphs
        feature_graphs = []
        for feature in requested_features:
            sys.stderr.write('Resolving requested feature: %s\n'%feature.name)
            possible_graphs = [graph for graph in iterGraphs(feature.name, provided_resources, set(), feature.args) if satisfiesRequest(graph, feature.resources)]
            if len(possible_graphs) == 0:
                raise ValueError('Unable to resolve a graph for requested feature: %s'%feature.name)
            elif len(possible_graphs) > 1:
                raise ValueError('Multiple solutions found for requested feature: %s'%feature.name)
            feature_graphs.append(possible_graphs)
            sys.stderr.write('Solution found\n\n')
        
        #missing_features = [feature.name for feature_graph, feature in izip(feature_graphs, requested_features) if len(feature_graph) == 0]
        #if len(missing_features) > 0:
        #    raise ValueError('Unable to resolve a graph for requested feature: %s'%','.join(missing_features))
        
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
    parser.add_argument('features', nargs='*', default=[],
        help='request a feature using the following format <name>[:<arguments>][:<resources>]')
    parser.add_argument('-j', '--job',
        help='specify a job file in json format')
    parser.add_argument('-o', '--output',
        help='direct output to named file (stdout)')
    parser.add_argument('-r', '--resources', nargs='+', default=[],
        help='provide a resource using the following format <file name>[;<type>][;<name>]')
    parser.add_argument('-t', '--template',
        help='specify a template string for the output')
    parser.add_argument('-y', '--type',
        help='specify the type of entity in the target file')
    parser.add_argument('-g', '--graph', action='store_true',
        help='do not run framework but print the resolved graph')
    parser.set_defaults(func=aggregate)

def aggregate(args):
    sys.stderr.write('\n    Ebias started...\n\n')
    
    if args.job:
        fhndl = open(args.job)
        job = json.load(fhndl)
        fhndl.close()
        requested_features =\
            [RequestedFeature(**ftr) for ftr in job['requested_features']]
        provided_resources = {res.name: res for res in\
            (ProvidedResource(**res) for res in job['provided_resources'])}
    else:
        requested_features = []
        provided_resources = {}
    
    requested_features.extend(ftr for ftr in parseRequestedFeatures(args.features))
    provided_resources.update(parseProvidedResources(args.input, args.resources))
    
    if len(requested_features) == 0:
        sys.stderr.write('Error: No features were requested. Please provide the names '\
            'of the features you wish to calculate.')
        sys.exit(1)
    
    aggregator = Aggregator()
    aggregator.aggregate(requested_features, provided_resources, args)

def parseRequestedFeatures(features):
    parser = FeatureParser()
    return [parser.parse(feature) for feature in features]
        
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
