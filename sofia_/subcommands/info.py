import argparse
import os

from lhc.tools import loadPlugins
from common import getProgramDirectory, loadActionHyperGraph
from sofia_.action import Action

def info(args):
    if args.output is None:
        import sys
        args.output = sys.stdout
    else:
        args.output = open(args.output, 'w')
    if args.graph:
        graphActions(args)
    else:
        listActions(args)
    args.output.close()

def listActions(args):
    program_dir = getProgramDirectory()
    action_dir = os.path.join(program_dir, 'steps')
    action_types = loadPlugins(action_dir, Action)
    
    if args.action is None:
        args.output.write('\nAvailable steps:\n===================\n')
        for name, action_type in sorted(action_types.iteritems()):
            if name in ('resource', 'dynamic_resource', 'static_resource'):
                continue
            listAction(action_type, args)
    else:
        listAction(action_types[args.action], args)

def listAction(action, args):
    args.output.write('%s\n'%action.__name__)
    if args.verbose:
        args.output.write(' Input:\n  %s\n'%', '.join(action.IN))
        args.output.write(' Output:\n  %s\n'%', '.join(action.OUT))
        if action.__doc__ is not None:
            args.output.write(' Description:\n  %s'%action.__doc__)
        args.output.write('\n')

def graphActions(args):
    graph = loadActionHyperGraph()
    args.output.write(str(graph))

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    defineParser(parser)
    return parser

def defineParser(parser):
    parser.add_argument('-g', '--graph', action='store_true',
        help='print out the hyper graph in DOT format (visualise with graphviz)')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='print out descriptions of each action')
    parser.add_argument('-o', '--output',
        help='specify where to put output')
    parser.add_argument('-f', '--action',
        help='list a specific action')
    parser.set_defaults(func=info)
    
if __name__ == '__main__':
    import sys
    sys.exit(main())
