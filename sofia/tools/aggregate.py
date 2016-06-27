import argparse
import os
import sys
import time
from collections import defaultdict

from common import get_program_directory
from sofia.attribute_map_factory import AttributeMapFactory
from sofia.error_manager import ERROR_MANAGER
from sofia.resolvers.entity_resolver import EntityResolver
from sofia.workflow.resolved_workflow import ResolvedWorkflow


class Aggregator(object):
    def __init__(self, template, workflow_template, stdout=sys.stdout):
        self.template = template
        self.workflow_template = workflow_template
        self.stdout = stdout

    def aggregate(self, requested_entities, provided_entities, args, maps=None):
        maps = {} if maps is None else maps

        sys.stderr.write('    Resolving worklow...\n')
        start_time = time.time()
        solution, matching_entities = self.resolve_requested_entities(requested_entities, provided_entities, maps)
        sys.stderr.write('\n    Workflow resolved in {} seconds.\n\n'.format(round(time.time() - start_time, 2)))
        if args.graph:
            self.stdout.write('{}\n\n'.format(solution))
            return

        sys.stderr.write('\n    Aggregating information...\n\n')
        if args.header is None:
            self.stdout.write('\t'.join(entity.alias for entity in requested_entities))
            self.stdout.write('\n')
        else:
            header = open(args.header).read() if os.path.exists(args.header) else args.header
            self.stdout.write(header)

        from sofia.execution_engines.simple_engine import SimpleExecutionEngine
        executor = SimpleExecutionEngine(solution)
        for entity in provided_entities:
            executor.resolve_entity(entity, list(entity.attributes['filename']))
        executor.execute()
        template = '\t'.join(['{}'] * len(requested_entities)) if args.template is None else args.template
        for fields in zip(*[executor.entities[entity] for entity in solution.heads]):
            self.stdout.write(template.format('' if field is None else str(field) for field in fields))
            self.stdout.write('\n')

        is_warning_header_written = False
        for step in solution.steps.itervalues():
            warnings = step.get_user_warnings()
            if len(warnings) > 0:
                if not is_warning_header_written:
                    is_warning_header_written = True
                    sys.stderr.write('\n    Warnings\n')
                sys.stderr.write('      Step: {}\n        '.format(step))
                sys.stderr.write('\n        '.join(warnings))
                sys.stderr.write('\n')

    def resolve_requested_entities(self, requested_entities, provided_entities, maps):
        solutions = [self.resolve_requested_entity(entity, provided_entities, maps) for entity in requested_entities]

        combined_solution = ResolvedWorkflow()
        for solution in solutions:
            combined_solution.add_entity_node(solution)

        return combined_solution, [solution.head for solution in solutions]

    def resolve_requested_entity(self, requested_entity, provided_entities, maps):
        def satisfies_request(graph, requested_resources):
            return graph.head.attributes['resource'].intersection(requested_resources) == requested_resources

        ERROR_MANAGER.reset()
        sys.stderr.write('     {} - '.format(requested_entity.name))
        solution_iterator = EntityResolver(requested_entity.name,
                                           self.template,
                                           provided_entities,
                                           maps,
                                           requested_entity.attributes['resource'])
        possible_graphs = list(solution_iterator)
        possible_graphs = [graph for graph in possible_graphs
                           if satisfies_request(graph, requested_entity.attributes['resource'])]
        if len(possible_graphs) == 0:
            sys.stderr.write('unable to resolve entity.\n\n')
            sys.stderr.write('     Possible reasons:\n')
            for error, names in sorted(ERROR_MANAGER.errors.iteritems()):
                sys.stderr.write('     * {}\n'.format(error))
                if len(names - {''}) > 0:
                    sys.stderr.write('       ')
                    sys.stderr.write('\n       '.join(names))
                    sys.stderr.write('\n')
            sys.exit(1)
        elif len(possible_graphs) == 1:
            sys.stderr.write('unique solution found\n')
            return possible_graphs[0]

        matching_graphs = defaultdict(list)
        for graph in possible_graphs:
            resources = frozenset([r for r in graph.head.attributes['resource'] if not r == 'target'])
            extra_resources = resources - requested_entity.attributes['resource']
            matching_graphs[len(extra_resources)].append((graph, extra_resources))
        count, matching_graphs = sorted(matching_graphs.iteritems())[0]
        unique = True
        if len(matching_graphs) > 1:
            match_size = defaultdict(list)
            for graph, extra_resources in matching_graphs:
                match_size[len(graph)].append((graph, extra_resources))
            matching_graphs = sorted(match_size.iteritems())[0][1]
            if len(matching_graphs) > 1:
                unique = False
        if not unique:
            sys.stderr.write('multiple solutions found.\n\n')
            for i, (graph, extra_resources) in enumerate(matching_graphs):
                sys.stderr.write('Solution {}:\n'.format(i))
                sys.stderr.write('{}\n\n'.format(str(graph)))
            sys.exit(1)
        matching_graph, extra_resources = matching_graphs[0]
        extra_resources = '\n      '.join(extra_resources)
        err = 'unique solution found.\n' if count == 0 else\
            'unique solution found with {} extra resources.\n      {}\n'.format(count, extra_resources)
        sys.stderr.write(err)
        return matching_graph


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
    add_arg('input', metavar='TARGET', nargs='+',
            help='the file to annotate')
    add_arg('-1', '--header',
            help='if specified use this header instead')
    add_arg('-e', '--entities', nargs='+', default=[], action='append',
            help='request an entity')
    add_arg('-E', '--entity-list',
            help='a text file with a list of requested entities')
    add_arg('-g', '--graph', action='store_true',
            help='do not run framework but print the resolved graph')
    add_arg('-m', '--maps', nargs='+', default=[],
            help='maps for converting for entity attributes')
    add_arg('-o', '--output',
            help='direct output to named file (default: stdout)')
    add_arg('-p', '--processes', default=None, type=int,
            help='the number of processes to run in parallel')
    add_arg('-r', '--resources', nargs='+', default=[], action='append',
            help='provide a resource')
    add_arg('-R', '--resource-list',
            help='a text file with a list of provided resources')
    add_arg('-s', '--simultaneous-entries', default=100, type=int,
            help='number of entries per worker')
    add_arg('-t', '--template',
            help='specify a template string for the output')
    add_arg('-w', '--workflow-template', default='genomics',
            help='specify a workflow template (default: genomics).')
    parser.set_defaults(func=aggregate)


def aggregate(args):
    import sys
    sys.stderr.write('\n    SoFIA started...\n\n')

    template_directory = os.path.join(get_program_directory(), 'templates', args.workflow_template)
    parser = EntityTypeParser(template_directory)

    provided_entities = parser.get_provided_entities(
        args.resources + [args.input + ['target']],
        args.resource_list
    )
    for entity in provided_entities:
        if 'sync' not in entity.attributes:
            entity.attributes['sync'] = {entity.alias}

    requested_entities = parser.get_requested_entities(args, provided_entities)
    if len(requested_entities) == 0:
        import sys
        sys.stderr.write('Error: No entities were requested. Please provide'
                         'the names of the entities you wish to calculate.')
        sys.exit(1)
    for entity in requested_entities:
        if 'resource' not in entity.attributes:
            entity.attributes['resource'] = set()
        entity.attributes['resource'].add('target')

    template_factory = TemplateFactory(template_directory)
    template = template_factory.make(provided_entities, requested_entities)

    stdout = sys.stdout if args.output is None else open(args.output, 'w')
    aggregator = Aggregator(template, args.workflow_template, stdout)
    maps = {k: AttributeMapFactory(v) for k, v in (map.split('=', 1) for map in args.maps)}
    aggregator.aggregate(requested_entities, provided_entities, args, maps)
    stdout.close()

if __name__ == '__main__':
    sys.exit(main())
