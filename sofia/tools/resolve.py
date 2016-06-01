from __future__ import with_statement

import argparse
import cPickle
import sys

from build import build, get_input
from collections import defaultdict
from sofia.workflow import ResolvedWorkflow
from sofia.error_manager import ERROR_MANAGER
from sofia.resolvers import EntityResolver, StepResolver


def resolve(template, requested_entities, provided_entities=None, maps=None):
    if len(requested_entities) == 0:
        raise ValueError('no entities requested')
    provided_entities = [] if provided_entities is None else provided_entities
    for entity in provided_entities:
        template.provide_entity(entity)
    maps = [] if maps is None else maps

    solution = ResolvedWorkflow()
    for entity in requested_entities:
        solution.add_entity_node(resolve_requested_entity(template, entity, maps))
    return solution


def resolve_requested_entity(template, entity, maps=None):
    def satisfies_request(graph, requested_resources):
        return graph.head.attributes['resource'].intersection(requested_resources) == requested_resources

    maps = [] if maps is None else maps

    ERROR_MANAGER.reset()
    sys.stderr.write('     {} - '.format(entity.name))
    solution_iterator = EntityResolver(entity.name, template, maps)
    possible_graphs = list(solution_iterator)
    possible_graphs = [graph for graph in possible_graphs
                       if satisfies_request(graph, entity.attributes['resource'])]
    if len(possible_graphs) == 0:
        sys.stderr.write('unable to resolve entity.\n\n')
        sys.stderr.write('     Possible reasons:\n')
        for error, names in sorted(ERROR_MANAGER.errors.iteritems()):
            sys.stderr.write('     * {}\n'.format(error))
            if len(names - {''}) > 0:
                sys.stderr.write('       ')
                sys.stderr.write('\n       '.join(names))
                sys.stderr.write('\n')
        sys.exit(1)
    elif len(possible_graphs) == 1:
        sys.stderr.write('unique solution found\n')
        return possible_graphs[0]

    matching_graphs = defaultdict(list)
    for graph in possible_graphs:
        resources = frozenset([r for r in graph.head.attributes['resource'] if not r == 'target'])
        extra_resources = resources - entity.attributes['resource']
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
    add_arg('-m', '--maps', nargs='+', default=[],
            help='maps for converting for entity attributes')
    add_arg('-o', '--output',
            help='direct output to named file (default: stdout)')
    add_arg('-p', '--pickled', action='store_true',
            help='output pickled template')
    add_arg('-t', '--target',
            help='name of implicit entity')
    add_arg('-w', '--workflow-template', default=['genomics'], nargs='+',
            help='specify a workflow template (default: genomics).')
    parser.set_defaults(func=resolve_init)


def resolve_init(args):
    input = get_input(args.input)
    template = build(input)

    provided_entities = [template.parser.parse_provided_entity(entity) for entity in args.resource]
    if args.resource_list:
        with open(args.resource_list) as fileobj:
            provided_entities.extend(template.parser.parse_provided_entity(line.split()) for line in fileobj)

    requested_entities = [template.parser.parse_requested_entity(definition) for definition in args.entity]
    if args.entity_list:
        with open(args.entity_list) as fileobj:
            requested_entities.extend(template.parser.parse_requested_entity(line.split()) for line in fileobj)

    if args.target is not None:
        for entity in requested_entities:
            if 'resource' not in entity.attributes:
                entity.attributes['resource'] = set()
            entity.attributes['resource'].add(args.target)

    output = sys.stdout
    if args.output is not None:
        filename = args.output + ('' if args.output.endswith('.sft') else '.sft')
        mode = 'wb' if args.pickled else 'w'
        output = open(filename, mode)
    workflow = resolve(template, requested_entities, provided_entities)
    if args.pickled:
        cPickle.dump(workflow, output, protocol=cPickle.HIGHEST_PROTOCOL)
    else:
        output.write(str(template))
    output.close()

if __name__ == '__main__':
    sys.exit(main())
