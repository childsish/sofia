import argparse
import json
import os
import sys

from collections import defaultdict
from common import getProgramDirectory, loadFeatureHyperGraph, loadEntityGraph
from ebias.error_manager import ERROR_MANAGER
from ebias.feature_parser import FeatureParser
from ebias.resource_parser import ResourceParser
from ebias.feature_graph import FeatureGraph

class Aggregator(object):
    def __init__(self):
        self.hyper_graph = loadFeatureHyperGraph()

    def aggregate(self, requested_features, provided_resources, args):
        sys.stderr.write('    Resolving features...\n')
        
        solution, resolved_features = self.resolveRequest(requested_features, provided_resources)
        if args.graph:
            sys.stdout.write('%s\n\n'%solution)
        else:
            sys.stderr.write('\n    Aggregating information...\n\n')
            solution.init()
            sys.stdout.write('\t'.join([str(ftr) for ftr in requested_features]))
            sys.stdout.write('\n')
            try:
                for row in solution.iterRows(resolved_features):
                    sys.stdout.write('\t'.join(row))
                    sys.stdout.write('\n')
            except TypeError:
                sys.stderr.write("A feature's format function does not return a string")
                sys.exit(1)

    def resolveRequest(self, requested_features, provided_resources):
        def satisfiesRequest(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources
        
        iterGraphs = self.hyper_graph.iterFeatureGraphs
        feature_graphs = []
        for feature in requested_features:
            ERROR_MANAGER.reset()
            sys.stderr.write('    %s - '%\
                str(feature))
            possible_graphs = [graph for graph in\
                iterGraphs(feature.name, feature, provided_resources)\
                if satisfiesRequest(graph, feature.resources)]
            if len(possible_graphs) == 0:
                sys.stderr.write('unable to resolve feature.\n')
                sys.stderr.write('      Possible reasons: \n      * %s\n'%\
                    '\n      * '.join(sorted(ERROR_MANAGER.errors)))
                sys.exit(1)
            elif len(possible_graphs) > 1:
                matching_graphs = defaultdict(list)
                for graph in possible_graphs:
                    resources = frozenset([r.name for r in graph.resources\
                        if not r.name == 'target'])
                    extra_resources = resources - feature.resources
                    matching_graphs[len(extra_resources)].append((graph, extra_resources))
                count, matching_graphs = sorted(matching_graphs.iteritems())[0]
                if len(matching_graphs) > 1:
                    for graph in possible_graphs:
                        sys.stderr.write('%s\n\n'%str(graph))
                    sys.stderr.write('    Multiple solutions found.\n')
                    sys.exit(1)
                matching_graph, extra_resources = matching_graphs[0]
                err = 'unique solution found.\n' if count == 0 else\
                    'unique solution found with %d extra resources.\n      %s\n'%(count, '\n      '.join(extra_resources))
                sys.stderr.write(err)
                feature_graphs.append(matching_graph)
            else:
                sys.stderr.write('unique solution found.\n')
                feature_graphs.append(possible_graphs[0])
        
        combined_graph = FeatureGraph()
        resolved_features = []
        for feature_graph in feature_graphs:
            combined_graph.update(feature_graph)
            resolved_features.append(feature_graph.feature.name)
        return combined_graph, resolved_features

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
    parser.add_argument('-F', '--feature-list',
        help='a text file with a list of requested features')
    parser.add_argument('-o', '--output',
        help='direct output to named file (stdout)')
    parser.add_argument('-r', '--resources', nargs='+', default=[],
        help='provide a resource using the following format <file name>[;<type>][;<name>]')
    parser.add_argument('-R', '--resource-list',
        help='a text file with a list of provided resources')
    parser.add_argument('-t', '--template',
        help='specify a template string for the output')
    parser.add_argument('-y', '--type',
        help='specify the type of entity in the target file')
    parser.add_argument('-g', '--graph', action='store_true',
        help='do not run framework but print the resolved graph')
    parser.set_defaults(func=aggregate)

def aggregate(args):
    sys.stderr.write('\n    Ebias started...\n\n')
    
    provided_resources = {}
    if args.resource_list is not None:
        fhndl = open(args.resource_list)
        provided_resources.update(parseProvidedResources(fhndl.read().split(),
            args.resources))
        fhndl.close()
    provided_resources.update(parseProvidedResources(args.input,
        args.resources))
    
    requested_features = [ftr for ftr in\
        parseRequestedFeatures(args.features, provided_resources)]
    if args.feature_list is not None:
        fhndl = open(args.feature_list)
        requested_features.extend(parseRequestedFeatures(fhndl.read().split(), provided_resources))
        fhndl.close()

    if len(requested_features) == 0:
        sys.stderr.write('Error: No features were requested. Please provide'\
            'the names of the features you wish to calculate.')
        sys.exit(1)
    
    aggregator = Aggregator()
    aggregator.aggregate(requested_features, provided_resources, args)
        
def parseProvidedResources(target, resources):
    program_dir = getProgramDirectory()
    fhndl = open(os.path.join(program_dir, 'config.json'))
    config = json.load(fhndl)
    fhndl.close()
    default_types = {type['ext']: type['type'] for type in config['default_types']}
    entity_graph = loadEntityGraph()
    resource_parser = ResourceParser(default_types, entity_graph)
    provided_resources = resource_parser.parseResources(resources)
    provided_resources['target'] = resource_parser.parseResource(target + ' -n target')
    return provided_resources

def parseRequestedFeatures(features, provided_resources):
    parser = FeatureParser(provided_resources)
    return [parser.parse(feature) for feature in features]

if __name__ == '__main__':
    sys.exit(main(sys.argv))
