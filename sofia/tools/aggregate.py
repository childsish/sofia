import argparse
import imp
import itertools
import multiprocessing
import os
import sys
import time
from collections import defaultdict

from common import get_provided_entities, get_requested_entities, get_program_directory
from sofia.attribute_map_factory import AttributeMapFactory
from sofia.error_manager import ERROR_MANAGER
from sofia.resolvers.entity_solution_iterator import EntitySolutionIterator
from sofia.template_factory import TemplateFactory
from sofia.graph.workflow import Workflow


class Aggregator(object):
    def __init__(self, hyper_graph, workflow_template, stdout=sys.stdout):
        self.hyper_graph = hyper_graph
        self.workflow_template = workflow_template
        self.stdout = stdout

    def aggregate(self, requested_entities, provided_entities, args, maps={}):
        def iter_target(target):
            params = {key: target.attr[key] for key in target.PARAMS if key in target.attr}
            target.init(**params)
            line_no = 1
            while True:
                yield target.calculate(), line_no
                line_no += 1

        sys.stderr.write('    Resolving entities...\n')

        start_time = time.time()
        solution, matching_entities = self.resolve_requested_entities(requested_entities, provided_entities, maps)
        sys.stderr.write('\n    Workflow resolved in {} seconds.\n\n'.format(round(time.time() - start_time, 2)))
        if args.graph:
            self.stdout.write('{}\n\n'.format(solution))
            return

        pool_iterator = iter_target(solution.steps['target'])
        initargs = [matching_entities, solution, self.hyper_graph.entity_graph]
        if args.processes == 1:
            init_worker(*initargs)
            it = itertools.imap(get_annotation, pool_iterator)
        else:
            pool = multiprocessing.Pool(args.processes, initializer=init_worker, initargs=initargs)
            it = pool.imap(get_annotation, pool_iterator, args.simultaneous_entries)

        sys.stderr.write('\n    Aggregating information...\n\n')
        if args.header is None:
            self.stdout.write('\t'.join(entity.alias for entity in requested_entities))
            self.stdout.write('\n')
        else:
            header = open(args.header).read() if os.path.exists(args.header) else args.header
            self.stdout.write(header)
        template = '\t'.join(['{}'] * len(requested_entities)) if args.template is None else args.template
        for row in it:
            row = [requested_entity.format(entity) for requested_entity, entity in zip(requested_entities, row)]
            self.stdout.write(template.format(*row))
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

        if args.processes > 1:
            pool.close()
            pool.join()

    def resolve_requested_entities(self, requested_entities, provided_entities, maps):
        solutions = [self.resolve_requested_entity(entity, provided_entities, maps) for entity in requested_entities]

        combined_solution = Workflow()
        for solution in solutions:
            combined_solution.join(solution)
        combined_solution.step = {step_graph.step.name for step_graph in solutions}

        matching_entities = self.get_matching_entities(solutions, requested_entities)
        return combined_solution, matching_entities

    def resolve_requested_entity(self, requested_entity, provided_entities, maps):
        def satisfies_request(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources

        ERROR_MANAGER.reset()
        sys.stderr.write('     {} - '.format(requested_entity.name))
        solution_iterator = EntitySolutionIterator(requested_entity.name,
                                                   self.hyper_graph,
                                                   provided_entities,
                                                   self.workflow_template,
                                                   maps,
                                                   requested_entity.resources, )
        possible_graphs = list(solution_iterator)
        possible_graphs = [graph for graph in possible_graphs
                           if satisfies_request(graph, requested_entity.resources)]
        if len(possible_graphs) == 0:
            sys.stderr.write('unable to resolve entity.\n\n')
            sys.stderr.write('     Possible reasons:\n     * ')
            sys.stderr.write('\n     * '.join(sorted(ERROR_MANAGER.errors)))
            sys.stderr.write('\n')
            sys.exit(1)
        elif len(possible_graphs) == 1:
            sys.stderr.write('unique solution found\n')
            return possible_graphs[0]

        matching_graphs = defaultdict(list)
        for graph in possible_graphs:
            resources = frozenset([r.alias for r in graph.resources if not r.name == 'target'])
            extra_resources = resources - {r.alias for r in requested_entity.resources}
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

    def get_matching_entities(self, solutions, requested_entities):
        return [solution.step.outs[entity.name] for solution, entity in zip(solutions, requested_entities)]


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
    if not os.path.exists(template_directory):
        file, template_directory, description = imp.find_module(args.workflow_template)
        if file:
            raise ImportError('not a package: %r', args.workflow_template)

    provided_entities = get_provided_entities(template_directory,
                                              args.resources + [args.input + ['target']],
                                              args.resource_list)
    requested_entities = get_requested_entities(args, provided_entities)
    if len(requested_entities) == 0:
        import sys
        sys.stderr.write('Error: No entities were requested. Please provide'
                         'the names of the entities you wish to calculate.')
        sys.exit(1)
    provided_entity_map = {entity.alias: entity for entity in provided_entities}
    target = provided_entity_map['target']
    for entity in requested_entities:
        if 'resource' in entity.attr:
            entity.attr['resource'] = entity.attr['resource'].split(',')
            for resource in entity.attr['resource']:
                entity.resources.add(provided_entity_map[resource])
        entity.resources.add(target)

    template_factory = TemplateFactory(template_directory)
    template = template_factory.make(provided_entities, requested_entities)

    stdout = sys.stdout if args.output is None else open(args.output, 'w')
    aggregator = Aggregator(template, args.workflow_template, stdout)
    maps = {k: AttributeMapFactory(v) for k, v in (map.split('=', 1) for map in args.maps)}
    aggregator.aggregate(requested_entities, provided_entities, args, maps)
    stdout.close()


requested_entities = None
solution = None
entity_graph = None
entities = None


def init_worker(requested_entities_, solution_, entity_graph_):
    global requested_entities
    global solution
    global entity_graph
    global entities

    requested_entities = requested_entities_
    solution = solution_
    entity_graph = entity_graph_
    entities = {}

    solution.init()


def get_annotation(target):
    """ Calculate the steps in this graph for each entity in the target resource. """
    global requested_entities
    global solution
    global entity_graph
    global entities

    for top_step in solution.step:
        solution.steps[top_step].reset(solution.steps)

    target, line_no = target
    target_parser = solution.steps['target']
    target = [target] if len(target_parser.outs) == 1 else target

    entities.update({str(key): value for key, value in zip(target_parser.outs.itervalues(), target)})
    solution.steps['target'].calculated = True

    for top_step in solution.step:
        try:
            solution.steps[top_step].generate(entities, solution.steps, entity_graph)
        except Exception, e:
            import sys
            import traceback
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            sys.stderr.write('Error processing entry on line {}\n'.format(solution.steps['target'].interface.line_no))
            #sys.exit(1)

    row = [entities.get(str(entity), '') for entity in requested_entities]
    return row

if __name__ == '__main__':
    sys.exit(main())