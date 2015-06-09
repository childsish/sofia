import argparse
import json
import os
import sys

from common import get_program_directory, parse_provided_resources, parse_requested_entities
from template_factory import TemplateFactory
from textwrap import wrap
from lhc.argparse import OpenWritableFile


def generate_graph(args):
    provided_resources = parse_provided_resources(args)
    template_factory = TemplateFactory(os.path.join(get_program_directory(), 'templates', args.workflow_template))
    template = template_factory.make(provided_resources)
    args.output.write(str(template))


def list_entities(args):
    program_dir = get_program_directory()
    fhndl = open(os.path.join(program_dir, 'templates', args.workflow_template, 'entities.json'))
    json_obj = json.load(fhndl)
    fhndl.close()

    res = []

    graph = load_step_hypergraph(args.workflow_template)
    for entity in json_obj:
        res.append(entity['name'])
        if 'description' in entity:
            res.append('\n'.join(wrap(entity['description'], initial_indent='    ', subsequent_indent='    ')))
    args.output.write('\n'.join(res))


def list_steps(args):
    provided_resources = parse_provided_resources(args)
    requested_entities = parse_requested_entities(args, provided_resources)
    template_factory = TemplateFactory(os.path.join(get_program_directory(), 'templates', args.workflow_template))
    template = template_factory.make(provided_resources, requested_entities)
    
    if args.step is None:
        args.output.write('\nAvailable steps (template: {}):\n==================\n'.format(args.workflow_template))
        for step in sorted(template.steps.itervalues(), key=lambda x: x.step_class.__name__):
            list_step(step.step_class, args)
    else:
        list_step(template.steps[args.step].step_class, args)


def list_step(step, args):
    args.output.write('{}\n'.format(step.__name__))
    if args.verbose:
        if len(step.IN) > 0:
            args.output.write(' Input:\n  {}\n'.format(', '.join(step.IN)))
        if len(step.OUT) > 0:
            args.output.write(' Output:\n  {}\n'.format(', '.join(step.OUT)))
        if step.__doc__ is not None:
            args.output.write(' Description:\n  {}\n'.format(step.__doc__.strip()))
        args.output.write('\n')


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    define_parser(parser)
    return parser


def define_parser(parser):
    subparsers = parser.add_subparsers()

    graph_parser = subparsers.add_parser('graph')
    graph_parser.add_argument('-e', '--entities', nargs='+', default=[])
    graph_parser.add_argument('-E', '--entity-list')
    graph_parser.add_argument('-r', '--resources', nargs='+', default=[])
    graph_parser.add_argument('-R', '--resource_list')
    graph_parser.add_argument('-t', '--target', dest='input', default=None,
                              help='specify the target resource')
    graph_parser.add_argument('-w', '--workflow-template', default='genomics',
                              help='specify a workflow template (default: genomics).')
    graph_parser.set_defaults(func=generate_graph)

    steps_parser = subparsers.add_parser('steps')
    steps_parser.add_argument('-s', '--step',
                              help='list a specific step')
    steps_parser.add_argument('-v', '--verbose', action='store_true',
                              help='print out descriptions of each step')
    steps_parser.add_argument('-w', '--workflow-template', default='genomics',
                              help='specify a workflow template (default: genomics).')
    steps_parser.set_defaults(func=list_steps)

    entity_parser = subparsers.add_parser('entity')
    entity_parser.add_argument('-e', '--entity',
                               help='list a specific entity')
    entity_parser.add_argument('-v', '--verbose', action='store_true',
                               help='print out descriptions of each entity')
    entity_parser.add_argument('-w', '--workflow-template', default='genomics',
                               help='specify a workflow template (default: genomics).')
    entity_parser.set_defaults(func=list_entities)

    parser.add_argument('-o', '--output', action=OpenWritableFile, default=sys.stdout,
                        help='specify where to put output')


if __name__ == '__main__':
    sys.exit(main())
