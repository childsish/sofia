import argparse
import itertools
import sys
import multiprocessing

from collections import defaultdict, OrderedDict
from common import load_step_hypergraph, load_entity_graph
from sofia_.error_manager import ERROR_MANAGER
from sofia_.parser import EntityParser, ResourceParser
from sofia_.graph.step_graph import StepGraph
from sofia_.resolvers.entity_solution_iterator import EntitySolutionIterator
from sofia_.attribute_map_factory import AttributeMapFactory
from sofia_.step.txt import TxtIterator
from sofia_.entity import Entity
from sofia_.step_wrapper import StepWrapper


class Aggregator(object):
    def __init__(self, workflow_template, requested_entities=[], custom_steps=[]):
        self.hyper_graph = load_step_hypergraph(workflow_template, requested_entities, custom_steps)
        self.workflow_template = workflow_template

    def aggregate(self, requested_entities, provided_resources, args, maps={}):
        def iter_target(target):
            target.init(**target.param)
            line_no = 1
            while True:
                yield target.calculate(), line_no
                line_no += 1

        sys.stderr.write('    Resolving entities...\n')

        solution, matching_entities = self.resolve_requested_entities(requested_entities, provided_resources, maps)
        if args.graph:
            sys.stdout.write('{}\n\n'.format(solution))
        else:
            sys.stderr.write('\n    Aggregating information...\n\n')
            if args.header is None:
                sys.stdout.write('\t'.join(entity.header for entity in requested_entities))
            else:
                sys.stdout.write(args.header)
            sys.stdout.write('\n')
        
            template = '\t'.join(['{}'] * len(requested_entities)) if args.template is None else args.template

            pool_iterator = iter_target(solution.steps['target'])
            initargs = [matching_entities, solution, self.hyper_graph.entity_graph]
            if args.processes == 1:
                init_worker(*initargs)
                it = itertools.imap(get_annotation, pool_iterator)
            else:
                pool = multiprocessing.Pool(args.processes, initializer=init_worker, initargs=initargs)
                it = pool.imap(get_annotation, pool_iterator, args.simultaneous_entries)

            for row in it:
                row = [requested_entity.format(entity) for requested_entity, entity in zip(requested_entities, row)]
                sys.stdout.write(template.format(*row))
                sys.stdout.write('\n')

            if args.processes > 1:
                pool.close()
                pool.join()

    def resolve_requested_entities(self, requested_entities, provided_resources, maps):
        solutions = [self.resolve_requested_entity(entity, provided_resources, maps) for entity in requested_entities]

        matching_entities = self.get_matching_entities(solutions, requested_entities)

        combined_solution = StepGraph()
        for solution in solutions:
            combined_solution.update(solution)
        combined_solution.step = {step_graph.step.name for step_graph in solutions}
        return combined_solution, matching_entities

    def resolve_requested_entity(self, requested_entity, provided_resources, maps):
        def satisfies_request(graph, requested_resources):
            return graph.resources.intersection(requested_resources) == requested_resources

        ERROR_MANAGER.reset()
        sys.stderr.write('    {} - '.format(requested_entity.name))
        solution_iterator = EntitySolutionIterator(requested_entity.name,
                                                   self.hyper_graph,
                                                   provided_resources,
                                                   self.workflow_template,
                                                   maps,
                                                   requested_entity.resources,)
        possible_graphs = list(solution_iterator)
        possible_graphs = [graph for graph in possible_graphs
                           if satisfies_request(graph, requested_entity.resources)]
        if len(possible_graphs) == 0:
            sys.stderr.write('unable to resolve entity.\n')
            sys.stderr.write('      Possible reasons:\n')
            sys.stderr.write('\n      * '.join(sorted(ERROR_MANAGER.errors)))
            sys.stderr.write('\n')
            sys.exit(1)
        elif len(possible_graphs) == 1:
            sys.stderr.write('unique solution found\n')
            return possible_graphs[0]

        matching_graphs = defaultdict(list)
        for graph in possible_graphs:
            resources = frozenset([r.name for r in graph.resources if not r.name == 'target'])
            extra_resources = resources - requested_entity.resources
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
            for graph in possible_graphs:
                sys.stderr.write('{}\n\n'.format(str(graph)))
            sys.stderr.write('    Multiple solutions found.\n')
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
    add_arg('input', metavar='TARGET',
            help='the file to annotate')
    add_arg('-1', '--header',
            help='if specified use this header instead')
    add_arg('-e', '--entities', nargs='+', default=[],
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
    add_arg('-r', '--resources', nargs='+', default=[],
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
    sys.stderr.write('\n    SoFIA started...\n\n')
    
    provided_resources = {}
    if args.resource_list is not None:
        fhndl = open(args.resource_list)
        resource_list = fhndl.read().strip().split('\n')
        fhndl.close()
        provided_resources.update(parse_provided_resources(args.input, resource_list, args.workflow_template))
    provided_resources.update(parse_provided_resources(args.input, args.resources, args.workflow_template))
    
    requested_entities = parse_requested_entities(args.entities, provided_resources)
    if args.entity_list is not None:
        fhndl = open(args.entity_list)
        entity_list = fhndl.read().strip().split('\n')
        fhndl.close()
        requested_entities.extend(parse_requested_entities(entity_list, provided_resources))

    if len(requested_entities) == 0:
        sys.stderr.write('Error: No entities were requested. Please provide'
                         'the names of the entities you wish to calculate.')
        sys.exit(1)

    maps = {k: AttributeMapFactory(v) for k, v in (map.split('=', 1) for map in args.maps)}

    custom_steps = []
    for name, resource in provided_resources.iteritems():
        if resource.format == 'custom_table':
            step = StepWrapper(TxtIterator,
                               outs=OrderedDict((out, Entity(out)) for out in resource.attr['out'].split(',') + ['target']),
                               param={'out_col': resource.attr['out_col']})
            custom_steps.append(step)
    
    aggregator = Aggregator(args.workflow_template, [entity.name for entity in requested_entities], custom_steps)
    aggregator.aggregate(requested_entities, provided_resources, args, maps)


def parse_provided_resources(target, resources, template):
    entity_graph = load_entity_graph(template)
    resource_parser = ResourceParser(entity_graph)
    provided_resources = resource_parser.parse_resources(resources)
    provided_resources['target'] = resource_parser.parse_resource(target + ' -n target')
    return provided_resources


def parse_requested_entities(steps, provided_resources):
    parser = EntityParser(provided_resources)
    return parser.parse_entity_requests(steps)


requested_entities = None
solution = None
entity_graph = None


def init_worker(requested_entities_, solution_, entity_graph_):
    global requested_entities
    global solution
    global entity_graph

    requested_entities = requested_entities_
    solution = solution_
    entity_graph = entity_graph_

    solution.init()


def get_annotation(target):
    """ Calculate the steps in this graph for each entity in the target
    resource. """
    global requested_entities
    global solution
    global entity_graph

    for top_step in solution.step:
        solution.steps[top_step].reset(solution.steps)

    target, line_no = target
    target_parser = solution.steps['target']
    target = [target] if len(target_parser.outs) == 1 else target

    entities = {str(key): value for key, value in zip(target_parser.outs.itervalues(), target)}
    solution.steps['target'].calculated = True

    for top_step in solution.step:
        try:
            solution.steps[top_step].generate(entities, solution.steps, entity_graph)
        except Exception:
            import sys
            import traceback
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            sys.stderr.write('Error processing entry on line {}\n'.format(solution.steps['target'].parser.line_no))
            #sys.exit(1)

    row = [entities[str(entity)] for entity in requested_entities]
    return row

if __name__ == '__main__':
    sys.exit(main())
