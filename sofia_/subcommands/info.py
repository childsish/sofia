import argparse
import os

from common import getProgramDirectory, loadActionHyperGraph, load_plugins
from sofia_.action import Action


def info(args):
    if args.output is None:
        import sys
        args.output = sys.stdout
    else:
        args.output = open(args.output, 'w')
    if args.graph:
        graph_actions(args)
    else:
        list_actions(args)
    args.output.close()


def list_actions(args):
    program_dir = getProgramDirectory()
    action_dir = os.path.join(program_dir, 'steps')
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
        args.output.write(' Input:\n  {}\n'.format(', '.join(action.IN)))
        args.output.write(' Output:\n  {}\n'.format(', '.join(action.OUT)))
        if action.__doc__ is not None:
            args.output.write(' Description:\n  {}'.format(action.__doc__))
        args.output.write('\n')


def graph_actions(args):
    graph = loadActionHyperGraph()
    args.output.write(str(graph))


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
    add_arg('-g', '--graph', action='store_true',
            help='print out the hyper graph in DOT format (visualise with graphviz)')
    add_arg('-v', '--verbose', action='store_true',
            help='print out descriptions of each action')
    add_arg('-o', '--output',
            help='specify where to put output')
    add_arg('-f', '--action',
            help='list a specific action')
    parser.set_defaults(func=info)


if __name__ == '__main__':
    import sys
    sys.exit(main())
