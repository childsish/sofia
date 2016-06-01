import argparse
import os
import sys

from sofia.template_factory import TemplateFactory


def build(template_directories):
    template_factory = TemplateFactory()
    for directory in template_directories:
        if not os.path.exists(directory):
            raise ValueError('{} does not exist'.format(directory))
        template_factory.add_root(directory)
    return template_factory.make()


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
            help='direct output to named file (default: stdout)')
    parser.set_defaults(func=build_init)


def build_init(args):
    program_directory = os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]
    input = []
    if len(args.input) == 0:
        input.append(os.path.join(program_directory, 'templates', 'genomics'))
    else:
        for directory in args.input:
            if os.path.exists(directory):
                pass
            elif os.path.exists(os.path.join(program_directory, 'templates', directory)):
                directory = os.path.join(program_directory, 'templates', directory)
            else:
                raise ValueError('{} does not exist'.format(directory))
            input.append(directory)

    output = sys.stdout if args.output is None else open(args.output, 'w')
    template = build(input)
    output.write(str(template))
    output.close()

if __name__ == '__main__':
    sys.exit(main())
