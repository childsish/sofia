import argparse
import json
import os
import sys

from common import get_program_directory, load_action_hypergraph, load_plugins
from sofia_.action import Action, Resource, Target
from textwrap import wrap
from lhc.argparse import OpenWritableFile


def generate_graph(args):
    graph = load_action_hypergraph()
    args.output.write(str(graph))


def list_entities(args):
    program_dir = get_program_directory()
    fhndl = open(os.path.join(program_dir, 'entities.json'))
    json_obj = json.load(fhndl)
    fhndl.close()

    res = []
    for entity, settings in json_obj.iteritems():
        res.append(entity)
        if 'description' in settings:
            res.append('\n'.join(wrap(settings['description'], initial_indent='    ', subsequent_indent='    ')))
    args.output.write('\n'.join(res))


def list_actions(args):
    action_classes = load_plugins(args.template, Action, {Resource, Target})
    
    if args.action is None:
        args.output.write('\nAvailable actions:\n==================\n')
        for action_class, template_name in sorted(action_classes, key=lambda x: x[0].__name__):
            list_action(action_class, template_name, args)
    else:
        for action_class, template_name in action_classes:
            if action_class.__name__ == args.action:
                list_action(action_class, template_name, args)


def list_action(action, template_name, args):
    args.output.write('{}\t({})\n'.format(action.__name__, template_name))
    if args.verbose:
        if len(action.IN) > 0:
            args.output.write(' Input:\n  {}\n'.format(', '.join(action.IN)))
        if len(action.OUT) > 0:
            args.output.write(' Output:\n  {}\n'.format(', '.join(action.OUT)))
        if action.__doc__ is not None:
            args.output.write(' Description:\n  {}\n'.format(action.__doc__.strip()))
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
    graph_parser.set_defaults(func=generate_graph)

    actions_parser = subparsers.add_parser('actions')
    actions_parser.add_argument('-a', '--action',
                                help='list a specific action')
    actions_parser.add_argument('-t', '--template', default='genomics',
                                help='list the defined template (default: genomics).')
    actions_parser.add_argument('-v', '--verbose', action='store_true',
                                help='print out descriptions of each action')
    actions_parser.set_defaults(func=list_actions)

    entity_parser = subparsers.add_parser('entity')
    entity_parser.add_argument('-e', '--entity',
                               help='list a specific entity')
    entity_parser.add_argument('-t', '--template', default='genomics',
                               help='list a specific entity')
    entity_parser.add_argument('-v', '--verbose', action='store_true',
                               help='print out descriptions of each entity')
    entity_parser.set_defaults(func=list_entities)

    parser.add_argument('-o', '--output', action=OpenWritableFile, default=sys.stdout,
                        help='specify where to put output')


if __name__ == '__main__':
    sys.exit(main())
