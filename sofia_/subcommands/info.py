import argparse
import json
import os
import sys

from common import get_program_directory, load_action_hypergraph, load_plugins
from sofia_.action import Action
from textwrap import wrap


class OutputAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, open(values, 'w'))


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
    action_dir = os.path.join(get_program_directory(), 'actions')
    action_types = load_plugins(action_dir, Action)
    
    if args.action is None:
        args.output.write('\nAvailable steps:\n===================\n')
        for name, action_type in sorted(action_types.iteritems()):
            if name in ('resource', 'dynamic_resource', 'static_resource'):
                continue
            list_action(action_type, args)
    else:
        list_action(action_types[args.action], args)


def list_action(action, args):
    args.output.write('{}\n'.format(action.__name__))
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

    action_parser = subparsers.add_parser('action')
    action_parser.add_argument('-v', '--verbose', action='store_true',
                               help='print out descriptions of each action')
    action_parser.add_argument('-a', '--action',
                               help='list a specific action')
    action_parser.set_defaults(func=list_actions)

    entity_parser = subparsers.add_parser('entity')
    entity_parser.add_argument('-v', '--verbose', action='store_true',
                               help='print out descriptions of each entity')
    entity_parser.add_argument('-e', '--entity',
                               help='list a specific entity')
    entity_parser.set_defaults(func=list_entities)

    parser.add_argument('-o', '--output', action=OutputAction, default=sys.stdout,
                        help='specify where to put output')


if __name__ == '__main__':
    sys.exit(main())
