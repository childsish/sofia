from __future__ import with_statement

import argparse
import sys

from build import build, get_input
from resolve import resolve
from sofia.execution_engines import SimpleExecutionEngine


def execute(workflow, engine=None):
    if engine is None:
        engine = SimpleExecutionEngine()
    engine.execute(workflow)


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
    parser.set_defaults(func=execute_init)


def execute_init(args):
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

    maps = {arg.split('=')[0]: arg.split('=')[1] for arg in args.maps}

    if args.target is not None:
        for entity in requested_entities:
            if 'resource' not in entity.attributes:
                entity.attributes['resource'] = set()
            entity.attributes['resource'].add(args.target)

    workflow = resolve(template, requested_entities, provided_entities, maps)
    output = sys.stdout if args.output is None else open(args.outpu, 'w')
    execute(workflow)
    output.close()

if __name__ == '__main__':
    sys.exit(main())
