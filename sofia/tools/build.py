import argparse
import cPickle
import os
import sys

from sofia.workflow_template import load_template


def build(template_directories):
    template = load_template(template_directories[0])
    for directory in template_directories[1:]:
        template.update(load_template(directory))
    return template


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
    add_arg('input', nargs='*',
            help='template directory(ies)')
    add_arg('-o', '--output',
            help='output to named .sft file (default: stdout)')
    add_arg('-p', '--pickled', action='store_true',
            help='output pickled template')
    parser.set_defaults(func=build_init)


def build_init(args):
    input = get_input(args.input)
    output = sys.stdout
    if args.output is not None:
        filename = args.output + ('' if args.output.endswith('.sft') else '.sft')
        mode = 'wb' if args.pickled else 'w'
        output = open(filename, mode)
    template = build(input)
    if args.pickled:
        cPickle.dump(template, output, protocol=cPickle.HIGHEST_PROTOCOL)
    else:
        output.write(str(template))
    output.close()


def get_input(args_input):
    program_directory = os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]
    input = []
    if len(args_input) == 0:
        input.append(os.path.join(program_directory, 'templates', 'genomics'))
    else:
        for directory in args_input:
            if os.path.exists(directory):
                pass
            elif os.path.exists(os.path.join(program_directory, 'templates', directory)):
                directory = os.path.join(program_directory, 'templates', directory)
            else:
                raise ValueError('{} does not exist'.format(directory))
            input.append(directory)
    return input

if __name__ == '__main__':
    sys.exit(main())
