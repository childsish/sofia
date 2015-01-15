import argparse
import json
import os
import sys
import multiprocessing

from collections import defaultdict
from common import get_program_directory, load_action_hypergraph, load_entity_graph
from sofia_.error_manager import ERROR_MANAGER
from sofia_.parser import EntityParser, ResourceParser
from sofia_.graph.action_graph import ActionGraph
from sofia_.resolvers.entity_solution_iterator import EntitySolutionIterator
from sofia_.attribute_map_factory import AttributeMapFactory


class Aggregator(object):
    def __init__(self):
        self.hyper_graph = load_action_hypergraph()

    def aggregate(self, requested_entities, provided_resources, args, maps={}):
        def iter_resource(resource):
            resource.init(**resource.param)
            line_no = 1
            while True:
                yield resource.calculate(), line_no
                line_no += 1

        sys.stderr.write('    Resolving entities...\n')
        
        solution, resolved_actions = self.resolve_request(requested_entities, provided_resources, maps)
        if args.graph:
            sys.stdout.write('{}\n\n'.format(solution))
        else:
            sys.stderr.write('\n    Aggregating information...\n\n')
            sys.stdout.write('\t'.join(map(str, requested_entities)))
            sys.stdout.write('\n')

            it = iter_resource(solution.actions['target'])
            pool = multiprocessing.Pool(args.processes, init_annotation, [resolved_actions, solution])
            for row in pool.imap(get_annotation, it, 100):
                sys.stdout.write('\t'.join(row))
                sys.stdout.write('\n')
            pool.close()
            pool.join()

    def resolve_request(self, requested_entities, provided_resources, maps):
        def satisfies_request(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources
        
        action_graphs = []
        for entity in requested_entities:
            ERROR_MANAGER.reset()
            sys.stderr.write('    {} - '.format(str(entity)))
            solution_iterator = EntitySolutionIterator(entity,
                                                       self.hyper_graph,
                                                       provided_resources,
                                                       maps,
                                                       entity.resources)
            possible_graphs = [graph for graph in solution_iterator
                               if satisfies_request(graph, entity.resources)]
            if len(possible_graphs) == 0:
                sys.stderr.write('unable to resolve entity.\n')
                reasons = '\n      * '.join(sorted(ERROR_MANAGER.errors))
                sys.stderr.write('      Possible reasons: \n      * {}\n'.format(reasons))
                sys.exit(1)
            elif len(possible_graphs) > 1:
                matching_graphs = defaultdict(list)
                for graph in possible_graphs:
                    resources = frozenset([r.name for r in graph.resources if not r.name == 'target'])
                    extra_resources = resources - entity.resources
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
                        sys.stderr.write('{}\n\n'.format(str(graph)))
                    sys.stderr.write('    Multiple solutions found.\n')
                    sys.exit(1)
                matching_graph, extra_resources = matching_graphs[0]
                extra_resources = '\n      '.join(extra_resources)
                err = 'unique solution found.\n' if count == 0 else\
                    'unique solution found with {} extra resources.\n      {}\n'.format(count, extra_resources)
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


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    define_parser(parser)
    return parser


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', metavar='TARGET',
            help='the file to annotate')
    add_arg('-e', '--entities', nargs='+', default=[],
            help='request an entity')
    add_arg('-E', '--entity-list',
            help='a text file with a list of requested entities')
    add_arg('-o', '--output',
            help='direct output to named file (default: stdout)')
    add_arg('-p', '--processes', default=None, type=int,
            help='the number of processes to run in parallel')
    add_arg('-r', '--resources', nargs='+', default=[],
            help='provide a resource')
    add_arg('-R', '--resource-list',
            help='a text file with a list of provided resources')
    add_arg('-t', '--template',
            help='specify a template string for the output')
    add_arg('-g', '--graph', action='store_true',
            help='do not run framework but print the resolved graph')
    add_arg('-m', '--maps', nargs='+', default=[],
            help='maps for converting for entity attributes')
    parser.set_defaults(func=aggregate)


def aggregate(args):
    sys.stderr.write('\n    SoFIA started...\n\n')
    
    provided_resources = {}
    if args.resource_list is not None:
        fhndl = open(args.resource_list)
        resource_list = fhndl.read().strip().split('\n')
        fhndl.close()
        provided_resources.update(parse_provided_resources(args.input, resource_list))
    provided_resources.update(parse_provided_resources(args.input, args.resources))
    
    requested_entities = parse_requested_entities(args.entities, provided_resources)
    if args.entity_list is not None:
        fhndl = open(args.entity_list)
        entity_list = fhndl.read().strip().split('\n')
        fhndl.close()
        requested_entities.extend(parse_requested_entities(entity_list, provided_resources))

    if len(requested_entities) == 0:
        sys.stderr.write('Error: No entities were requested. Please provide'
                         'the names of the entities you wish to calculate.')
        sys.exit(1)

    maps = {k: AttributeMapFactory(v) for k, v in (map.split('=', 1) for map in args.maps)}
    
    aggregator = Aggregator()
    aggregator.aggregate(requested_entities, provided_resources, args, maps)


def parse_provided_resources(target, resources):
    program_dir = get_program_directory()
    fhndl = open(os.path.join(program_dir, 'config.json'))
    config = json.load(fhndl)
    fhndl.close()
    default_types = {type['ext']: type['type'] for type in config['default_types']}
    entity_graph = load_entity_graph()
    resource_parser = ResourceParser(default_types, entity_graph)
    provided_resources = resource_parser.parse_resources(resources)
    provided_resources['target'] = resource_parser.parse_resource(target + ' -n target')
    return provided_resources


def parse_requested_entities(actions, provided_resources):
    parser = EntityParser(provided_resources)
    return parser.parse_entity_requests(actions)


requested_actions = None
solution = None


def init_annotation(req_ftr, sol):
    global requested_actions
    global solution
    requested_actions = req_ftr
    solution = sol
    solution.init()


def get_annotation(target):
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
        except Exception:
            import sys
            import traceback
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            sys.stderr.write('Error processing entry on line {}\n'.format(solution.actions['target'].parser.line_no))
            sys.exit(1)
    return row
    #try:
    #    sys.stdout.write('\t'.join(row))
    #except TypeError:
    #    sys.stderr.write("A action's format function does not return a string")
    #    sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
