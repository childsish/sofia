import argparse
import os
import sys
from textwrap import wrap


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def generate_graph(workflow_template, output=sys.stdout):
    template_directory = os.path.join(get_program_directory(), 'templates', workflow_template)
    template_factory = TemplateFactory(template_directory)
    template = template_factory.make()
    output.write(str(template))


def list_entities(workflow_template, output=sys.stdout):
    template_directory = os.path.join(get_program_directory(), 'templates', workflow_template)

    template_factory = TemplateFactory(template_directory)
    template = template_factory.make()

    for entity in sorted(template.entity_graph.entities.values(), key=lambda x: x['name']):
        output.write(entity['name'])
        output.write('\n')
        if 'description' in entity:
            output.write('\n'.join(wrap(entity['description'], initial_indent='    ', subsequent_indent='    ')))
            output.write('\n')


def list_steps(workflow_template, step=None, output=sys.stdout, verbose=False):
    template_directory = os.path.join(get_program_directory(), 'templates', workflow_template)
    template_factory = TemplateFactory(template_directory)
    template = template_factory.make([])

    if step is None:
        output.write('\nAvailable steps (template: {}):\n==================\n'.format(workflow_template))
        for step in sorted(template.steps.values(), key=lambda x: x.step_class.__name__):
            list_step(step.step_class, output, verbose)
    else:
        list_step(template.steps[step].step_class, output, verbose)


def list_step(step, output=sys.stdout, verbose=False):
    output.write('{}\n'.format(step.__name__))
    if verbose:
        if len(step.IN) > 0:
            output.write(' Input:\n  {}\n'.format(', '.join(step.IN)))
        if len(step.OUT) > 0:
            output.write(' Output:\n  {}\n'.format(', '.join(step.OUT)))
        if step.__doc__ is not None:
            output.write(' Description:\n  {}\n'.format(step.__doc__.strip()))
        output.write('\n')


def main():
    import sys
    parser = get_parser()
    args = parser.parse_args()
    if args.output is None:
        args.output = sys.stdout
    else:
        args.output = open(args.output, 'w')
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
    graph_parser.add_argument('-o', '--output',
                              help='output destination (default: stdout)')
    graph_parser.add_argument('-t', '--target', dest='input', default=None,
                              help='specify the target resource')
    graph_parser.add_argument('-w', '--workflow-template', default='genomics',
                              help='specify a workflow template (default: genomics).')
    graph_parser.set_defaults(func=info_graph_init)

    entity_parser = subparsers.add_parser('entity')
    entity_parser.add_argument('-e', '--entity',
                               help='list a specific entity')
    entity_parser.add_argument('-v', '--verbose', action='store_true',
                               help='print out descriptions of each entity')
    entity_parser.add_argument('-w', '--workflow-template', default='genomics',
                               help='specify a workflow template (default: genomics).')
    entity_parser.set_defaults(func=info_entity_init)

    steps_parser = subparsers.add_parser('steps')
    steps_parser.add_argument('-s', '--step',
                              help='list a specific step')
    steps_parser.add_argument('-v', '--verbose', action='store_true',
                              help='print out descriptions of each step')
    steps_parser.add_argument('-w', '--workflow-template', default='genomics',
                              help='specify a workflow template (default: genomics).')
    steps_parser.set_defaults(func=info_steps_init)

    parser.add_argument('-o', '--output',
                        help='specify where to put output')


def info_graph_init(args):
    output = sys.stdout if args.output is None else open(args.output, 'w')
    generate_graph(args.workflow_template, output)
    output.close()


def info_entity_init(args):
    output = sys.stdout if args.output is None else open(args.output, 'w')
    list_entities(args.workflow_template, output)
    output.close()


def info_steps_init(args):
    output = sys.stdout if args.output is None else open(args.output, 'w')
    list_steps(args.workflow_template, args.step, output, args.verbose)
    output.close()


if __name__ == '__main__':
    sys.exit(main())
