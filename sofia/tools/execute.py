import argparse
import sys

from sofia.tools.build import build, get_input
from sofia.tools.resolve import resolve, parse_entity_list
from sofia.execution_engines.low_memory_engine import LowMemoryExecutionEngine#, ParallelEngine


def execute(workflow, engine=None):
    """
    Execute a workflow using the given engine.

    :param workflow: Workflow to be executed
    :param engine: Engine used to execute workflow. Default: LowMemoryExecutionEngine
    """
    if engine is None:
        engine = LowMemoryExecutionEngine(256)
    engine.execute(workflow)


def main():
    parser = get_parser()
    args = parser.parse_args()
    return args.func(args)


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
    parser.set_defaults(func=init_execute)


def init_execute(args):
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

    workflow = resolve(template, requested_entities, provided_entities, args.maps)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    execute(workflow)
    output.close()

if __name__ == '__main__':
    sys.exit(main())
