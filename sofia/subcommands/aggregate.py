import argparse
import json
import os
import sys
import multiprocessing

from collections import defaultdict
from common import getProgramDirectory, loadFeatureHyperGraph, loadEntityGraph
from functools import partial
from sofia.error_manager import ERROR_MANAGER
from sofia.parser import FeatureParser, ResourceParser
from sofia.feature_graph import FeatureGraph
from sofia.solution_iterator import SolutionIterator
from sofia.feature_wrapper import FeatureWrapper
from sofia.attribute_map_factory import AttributeMapFactory

class Aggregator(object):
    def __init__(self):
        self.hyper_graph = loadFeatureHyperGraph()

    def aggregate(self, requested_features, provided_resources, args, maps={}):
        def iterResource(resource):
            resource.init(**resource.param)
            line_no = 1
            while True:
                yield resource.calculate(), line_no
                line_no += 1

        sys.stderr.write('    Resolving features...\n')
        
        solution, resolved_features = self.resolveRequest(requested_features, provided_resources, maps)
        if args.graph:
            sys.stdout.write('%s\n\n'%solution)
        else:
            sys.stderr.write('\n    Aggregating information...\n\n')
            sys.stdout.write('\t'.join(map(str, requested_features)))
            sys.stdout.write('\n')

            it = iterResource(solution.features['target'])
            pool = multiprocessing.Pool(args.processes, initAnnotation,
                [resolved_features, solution])
            for row in pool.imap(getAnnotation, it, 100):
                sys.stdout.write('\t'.join(row))
                sys.stdout.write('\n')
            pool.close()
            pool.join()

    def resolveRequest(self, requested_features, provided_resources, maps):
        def satisfiesRequest(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources
        
        feature_graphs = []
        for feature in requested_features:
            ERROR_MANAGER.reset()
            sys.stderr.write('    %s - '%\
                str(feature))
            old_feature_wrapper = self.hyper_graph.features[feature.name]
            feature_wrapper = FeatureWrapper(old_feature_wrapper.feature_class,
                old_feature_wrapper.name,
                old_feature_wrapper.ins,
                old_feature_wrapper.outs,
                feature.param,
                feature.attr)
            solution_iterator = SolutionIterator(feature_wrapper, self.hyper_graph, provided_resources, maps)
            possible_graphs = [graph for graph in solution_iterator\
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
    parser.add_argument('-p', '--processes', default=1, type=int,
        help='the number of processes to run in parallel')
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
    parser.add_argument('-m', '--maps', nargs='+', default=[],
        help='maps for converting for entity attributes')
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
    
    requested_features = parseRequestedFeatures(args.features, provided_resources)
    if args.feature_list is not None:
        fhndl = open(args.feature_list)
        requested_features.extend(parseRequestedFeatures(fhndl.read().split('\n'), provided_resources))
        fhndl.close()

    if len(requested_features) == 0:
        sys.stderr.write('Error: No features were requested. Please provide'\
            'the names of the features you wish to calculate.')
        sys.exit(1)

    maps = {k: AttributeMapFactory(v) for k, v in (map.split('=', 1) for map in args.maps)}
    
    aggregator = Aggregator()
    aggregator.aggregate(requested_features, provided_resources, args, maps)
        
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
    return parser.parseFeatures(features)


requested_features = None
solution = None

def initAnnotation(req_ftr, sol):
    global requested_features
    global solution
    requested_features = req_ftr
    solution = sol

    solution.init()

def getAnnotation(target):
    """ Calculate the features in this graph for each entity in the target
    resource. """
    global requested_features
    global solution

    for feature in requested_features:
        solution.features[feature].reset(solution.features)
    target, line_no = target
    kwargs = {'target': target}
    row = []
    for feature in requested_features:
        try:
            item = solution.features[feature].generate(kwargs, solution.features)
            item = '' if item is None else solution.features[feature].format(item)
            row.append(item)
        except Exception, e:
            import sys
            import traceback
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            sys.stderr.write('Error processing entry on line %d\n'%\
                (solution.features['target'].parser.line_no))
            sys.exit(1)
    return row
    #try:
    #    sys.stdout.write('\t'.join(row))
    #except TypeError:
    #    sys.stderr.write("A feature's format function does not return a string")
    #    sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
