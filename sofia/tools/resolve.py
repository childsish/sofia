import argparse
import pickle
import sys

from sofia.tools.build import build, get_input
from collections import defaultdict
from sofia.workflow import ResolvedWorkflow, EntityNode, StepNode
from sofia.error_manager import ERROR_MANAGER
from sofia.resolvers import EntityResolver
from sofia.step import ConcreteStep, Writer
from sofia.entity_type import EntityType


def resolve(template, requested_entities, provided_entities=None, maps=None):
    if len(requested_entities) == 0:
        raise ValueError('no entities requested')
    provided_entities = [] if provided_entities is None else provided_entities
    for entity in provided_entities:
        template.provide_entity(entity)

    maps = initialise_maps(maps)

    if any(not entity.name.endswith('_file') for entity in requested_entities):
        ins = [entity for entity in requested_entities if not entity.name.endswith('_file')]
        output_step = ConcreteStep(Writer, ins=ins, outs=['txt_file'], params={'entities': ins})
        step_node = StepNode(output_step, {})

    partial_solutions = []
    for entity in requested_entities:
        partial_solution = resolve_requested_entity(template, entity, maps)
        if entity.name.endswith('_file'):
            partial_solutions.append(partial_solution)
        else:
            step_node.add_entity_node(partial_solution)

    if any(not entity.name.endswith('_file') for entity in requested_entities):
        entity_node = EntityNode(EntityType('txt_file'))
        entity_node.add_step_node(step_node)
        partial_solutions.append(entity_node)

    solution = ResolvedWorkflow(template.provided_entities)
    for partial_solution in partial_solutions:
        solution.add_entity_node(partial_solution)
    return solution


def initialise_maps(maps=None):
    res = {}
    if maps is None:
        return res
    for map in maps:
        if len(map) < 2:
            msg = 'Map "{}" was improperly defined. It requires at least the attribute name and filename, and optionally several parameters'
            raise ValueError(msg.format(' '.join(map)))
        res[map[0]] = dict(part.split('=', 1) for part in map[2:])
        res[map[0]]['map_file'] = map[1]
    return res


def resolve_requested_entity(template, entity, maps=None):

    def satisfies_request(request, response):
        res = response['resource'].intersection(request['resource']) == request['resource'] and \
              (not 'sync' in request or request['sync'] == response['sync'])
        return response['resource'].intersection(request['resource']) == request['resource'] and \
               (not 'sync' in request or request['sync'] == response['sync'])

    maps = {} if maps is None else maps

    ERROR_MANAGER.reset()
    sys.stderr.write('     {} - '.format(entity.name))
    solution_iterator = EntityResolver(entity.name, template, maps=maps, requested_resources=entity.attributes.get('resource', set()))
    possible_graphs = list(solution_iterator)
    possible_graphs = [graph for graph in possible_graphs if satisfies_request(entity.attributes, graph.head.attributes)]
    if len(possible_graphs) == 0:
        sys.stderr.write('unable to resolve entity.\n\n')
        sys.stderr.write('     Possible reasons:\n')
        for error, names in sorted(ERROR_MANAGER.errors.items()):
            sys.stderr.write('     * {}'.format(error))
            if len(names - {''}) > 0:
                sys.stderr.write('\n            when resolving\n')
                sys.stderr.write('       ')
                sys.stderr.write('\n       '.join(names))
                sys.stderr.write('\n')
            else:
                sys.stderr.write('\n')
        sys.exit(1)
    elif len(possible_graphs) == 1:
        sys.stderr.write('unique solution found\n')
        return possible_graphs[0]

    # Pick the graphs with the least extra resources
    matching_graphs = defaultdict(list)
    for graph in possible_graphs:
        resources = frozenset([r for r in graph.head.attributes['resource'] if not r == 'target'])
        extra_resources = resources - entity.attributes['resource']
        matching_graphs[len(extra_resources)].append((graph, extra_resources))
    count, matching_graphs = sorted(matching_graphs.items())[0]

    # Pick the graphs with the
    unique = True
    if len(matching_graphs) > 1:
        match_size = defaultdict(list)
        for graph, extra_resources in matching_graphs:
            match_size[len(graph)].append((graph, extra_resources))
        matching_graphs = sorted(match_size.items())[0][1]
        if len(matching_graphs) > 1:
            unique = False
    if not unique:
        sys.stderr.write('multiple solutions found.\n\n')
        for i, (graph, extra_resources) in enumerate(matching_graphs):
            sys.stderr.write('Solution {}:\n'.format(i))
            sys.stderr.write('{}\n\n'.format(str(graph)))
        sys.exit(1)
    matching_graph, extra_resources = matching_graphs[0]
    extra_resources = '\n      '.join(extra_resources)
    err = 'unique solution found.\n' if count == 0 else\
        'unique solution found with {} extra resources.\n      {}\n'.format(count, extra_resources)
    sys.stderr.write(err)
    return matching_graph


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    define_parser(parser)
    return parser


def define_parser(parser):
    add_arg = parser.add_argument_group('input').add_argument
    add_arg('input', nargs='*',
            help='template directory(ies)')
    add_arg('-e', '--entity', nargs='+', default=[], action='append',
            help='request an entity')
    add_arg('-E', '--entity-list',
            help='text file with a list of requested entities')
    add_arg('-r', '--resource', nargs='+', default=[], action='append',
            help='provide a resource')
    add_arg('-R', '--resource-list',
            help='text file with a list of provided resources')

    add_arg = parser.add_argument_group('miscellaneous').add_argument
    add_arg('-m', '--maps', nargs='+', default=[], action='append',
            help='maps for converting for entity attributes')
    add_arg('-o', '--output',
            help='direct output to named file (default: stdout)')
    add_arg('-p', '--pickled', action='store_true',
            help='output pickled template')
    add_arg('-t', '--target',
            help='name of implicit entity')
    add_arg('-w', '--workflow-template', default=['genomics'], nargs='+',
            help='specify a workflow template (default: genomics).')
    parser.set_defaults(func=init_resolve)


def init_resolve(args):
    import os
    
    input = get_input(args.input)
    template = build(input)

    provided_entities = [template.parser.parse_provided_entity(entity) for entity in args.resource]
    if args.resource_list:
        provided_entities.extend(parse_entity_list(args.resource_list, template.parser.parse_provided_entity))

    for entity in provided_entities:
        filename = next(iter(entity.attributes['filename']))
        if not os.path.exists(filename):
            sys.stderr.write('No such file or directory \'{}\'.\n'.format(filename))
            sys.exit(1)

    requested_entities = [template.parser.parse_requested_entity(definition) for definition in args.entity]
    if args.entity_list:
        requested_entities.extend(parse_entity_list(args.entity_list, template.parser.parse_requested_entity))

    if args.target is not None:
        for entity in requested_entities:
            if 'resource' not in entity.attributes:
                entity.attributes['resource'] = set()
            if 'sync' not in entity.attributes:
                entity.attributes['sync'] = set()
            entity.attributes['resource'].add(args.target)
            entity.attributes['sync'].add(args.target)

    output = sys.stdout
    if args.output is not None:
        filename = args.output + ('' if args.output.endswith('.sfw') else '.sfw')
        mode = 'wb' if args.pickled else 'w'
        output = open(filename, mode)
    workflow = resolve(template, requested_entities, provided_entities, args.maps)
    if args.pickled:
        pickle.dump(workflow, output, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        output.write(str(workflow))
    output.close()


def parse_entity_list(filename, parse_function):
    entities = []
    with open(filename) as fileobj:
        for line in fileobj:
            if line.strip() == '':
                continue

            try:
                entity = parse_function(line.strip().split())
            except Exception as e:
                sys.stderr.write(str(e) + '\n')
                return 1
            entities.append(entity)
    return entities


if __name__ == '__main__':
    sys.exit(main())
