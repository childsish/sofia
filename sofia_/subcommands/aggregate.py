import argparse
import json
import os
import sys
import multiprocessing
from collections import defaultdict

from common import getProgramDirectory, loadActionHyperGraph, loadEntityGraph
from sofia_.error_manager import ERROR_MANAGER
from sofia_.parser import ActionParser, ResourceParser
from sofia_.graph.action_graph import ActionGraph
from resolvers.action_solution_iterator import ActionSolutionIterator
from sofia_.action_wrapper import ActionWrapper
from sofia_.attribute_map_factory import AttributeMapFactory


class Aggregator(object):
    def __init__(self):
        self.hyper_graph = loadActionHyperGraph()

    def aggregate(self, requested_actions, provided_resources, args, maps={}):
        def iterResource(resource):
            resource.init(**resource.param)
            line_no = 1
            while True:
                yield resource.calculate(), line_no
                line_no += 1

        sys.stderr.write('    Resolving steps...\n')
        
        solution, resolved_actions = self.resolve_request(requested_actions, provided_resources, maps)
        if args.graph:
            sys.stdout.write('%s\n\n'%solution)
        else:
            sys.stderr.write('\n    Aggregating information...\n\n')
            sys.stdout.write('\t'.join(map(str, requested_actions)))
            sys.stdout.write('\n')

            it = iterResource(solution.actions['target'])
            pool = multiprocessing.Pool(args.processes, initAnnotation,
                [resolved_actions, solution])
            for row in pool.imap(getAnnotation, it, 100):
                sys.stdout.write('\t'.join(row))
                sys.stdout.write('\n')
            pool.close()
            pool.join()

    def resolve_request(self, requested_actions, provided_resources, maps):
        def satisfies_request(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources
        
        action_graphs = []
        for action in requested_actions:
            ERROR_MANAGER.reset()
            sys.stderr.write('    %s - ' % str(action))
            old_action_wrapper = self.hyper_graph.actions[action.name]
            action_wrapper = ActionWrapper(old_action_wrapper.action_class,
                                           old_action_wrapper.name,
                                           old_action_wrapper.ins,
                                           old_action_wrapper.outs,
                                           action.param,
                                           action.attr)
            solution_iterator = ActionSolutionIterator(action_wrapper,
                                                 self.hyper_graph,
                                                 provided_resources,
                                                 maps,
                                                 action.resources)
            possible_graphs = [graph for graph in solution_iterator
                               if satisfies_request(graph, action.resources)]
            if len(possible_graphs) == 0:
                sys.stderr.write('unable to resolve action.\n')
                sys.stderr.write('      Possible reasons: \n      * %s\n' %
                                 '\n      * '.join(sorted(ERROR_MANAGER.errors)))
                sys.exit(1)
            elif len(possible_graphs) > 1:
                matching_graphs = defaultdict(list)
                for graph in possible_graphs:
                    resources = frozenset([r.name for r in graph.resources\
                        if not r.name == 'target'])
                    extra_resources = resources - action.resources
                    matching_graphs[len(extra_resources)].append((graph, extra_resources))
                count, matching_graphs = sorted(matching_graphs.iteritems())[0]
                unique = True
                if len(matching_graphs) > 1:
                    match_size = defaultdict(list)
                    for graph, extra_resources in matching_graphs:
                        match_size[len(graph)].append((graph, extra_resources))
                    matching_graphs = sorted(match_size.iteritems())[0][1]
                    if len(matching_graphs) > 1:
                        unique = False
                if not unique:
                    for graph in possible_graphs:
                        sys.stderr.write('%s\n\n'%str(graph))
                    sys.stderr.write('    Multiple solutions found.\n')
                    sys.exit(1)
                matching_graph, extra_resources = matching_graphs[0]
                err = 'unique solution found.\n' if count == 0 else\
                    'unique solution found with %d extra resources.\n      %s\n'%(count, '\n      '.join(extra_resources))
                sys.stderr.write(err)
                action_graphs.append(matching_graph)
            else:
                sys.stderr.write('unique solution found.\n')
                action_graphs.append(possible_graphs[0])
        
        combined_graph = ActionGraph()
        resolved_actions = []
        for action_graph in action_graphs:
            combined_graph.update(action_graph)
            resolved_actions.append(action_graph.action.name)
        return combined_graph, resolved_actions

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
    parser.add_argument('actions', nargs='*', default=[],
        help='request a action using the following format <name>[:<arguments>][:<resources>]')
    parser.add_argument('-A', '--action-list',
        help='a text file with a list of requested steps')
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
        resource_list = fhndl.read().strip().split('\n')
        fhndl.close()
        provided_resources.update(parseProvidedResources(args.input,
            resource_list))
    provided_resources.update(parseProvidedResources(args.input,
        args.resources))
    
    requested_actions = parseRequestedActions(args.actions, provided_resources)
    if args.action_list is not None:
        fhndl = open(args.action_list)
        action_list = fhndl.read().strip().split('\n')
        requested_actions.extend(parseRequestedActions(action_list, provided_resources))
        fhndl.close()

    if len(requested_actions) == 0:
        sys.stderr.write('Error: No steps were requested. Please provide'\
            'the names of the steps you wish to calculate.')
        sys.exit(1)

    maps = {k: AttributeMapFactory(v) for k, v in (map.split('=', 1) for map in args.maps)}
    
    aggregator = Aggregator()
    aggregator.aggregate(requested_actions, provided_resources, args, maps)
        
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

def parseRequestedActions(actions, provided_resources):
    parser = ActionParser(provided_resources)
    return parser.parseActions(actions)


requested_actions = None
solution = None

def initAnnotation(req_ftr, sol):
    global requested_actions
    global solution
    requested_actions = req_ftr
    solution = sol

    solution.init()

def getAnnotation(target):
    """ Calculate the steps in this graph for each entity in the target
    resource. """
    global requested_actions
    global solution

    for action in requested_actions:
        solution.actions[action].reset(solution.actions)
    solution.actions['target'].calculated = True
    target, line_no = target
    kwargs = {'target': target}
    row = []
    for action in requested_actions:
        try:
            item = solution.actions[action].generate(kwargs, solution.actions)
            item = '' if item is None else solution.actions[action].format(item)
            row.append(item)
        except Exception, e:
            import sys
            import traceback
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            sys.stderr.write('Error processing entry on line %d\n'%\
                (solution.actions['target'].parser.line_no))
            sys.exit(1)
    return row
    #try:
    #    sys.stdout.write('\t'.join(row))
    #except TypeError:
    #    sys.stderr.write("A action's format function does not return a string")
    #    sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
