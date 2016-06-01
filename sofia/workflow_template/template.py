from entity_set import EntitySet
from lhc.graph import NPartiteGraph
from sofia.step import Extractor, Converter
from sofia.workflow_template.entity_definition_parser import EntityDefinitionParser


class Template(NPartiteGraph):
    """
    A template from which workflows can be resolved. This is built from user defined steps and can also contain
    provided entities. In fact, all input is considered a template that may contain steps and/or data. Template can then
    be merged to provide a master template for resolution.
    """

    ENTITY_PARTITION = 0
    STEP_PARTITION = 1

    """ A hyper graph of all the possible step calculation pathways. """
    def __init__(self, entities=None, steps=None, attributes=None, parser=None):
        super(Template, self).__init__()
        self.provided_entities = {}

        self.entities = EntitySet() if entities is None else entities
        self.steps = {} if steps is None else steps
        self.attributes = {} if attributes is None else attributes
        self.parser = EntityDefinitionParser({}) if parser is None else parser

        self.register_entities(entities)
        self.register_steps(steps)
        self.register_attribute(attributes)

    def __str__(self):
        """ Convert to string

        :return: A string representing the graph in Graphviz format.
        """
        res = ['digraph {} {{'.format(self.name)]
        for entity in sorted(self.partitions[self.ENTITY_PARTITION]):
            res.append('    "{}" [shape=box];'.format(entity))
        for e, v in sorted(self.graph.es.iteritems()):
            if v.fr in self.steps and self.steps[v.fr].step_class in {Extractor, Converter}:
                continue
            elif v.to in self.steps and self.steps[v.to].step_class in {Extractor, Converter}:
                continue
            res.append('    "{}" -> "{}";'.format(v.fr, v.to))
        for entity in self.entities.entities.itervalues():
            if 'is_a' in entity:
                res.append('    "{}" -> "{}" [color=red,type=dotted,label="is_a"]'.format(entity['name'], entity['is_a']))
            if 'has_a' in entity:
                for has_a in entity['has_a']:
                    res.append('    "{}" -> "{}" [color=blue,type=dotted,label="has_a"]'.format(entity['name'], has_a))
        res.append('}')
        return '\n'.join(res)

    def register_entities(self, entities):
        provided = {}
        for entity in entities.entities.itervalues():
            self.add_vertex(entity['name'], self.ENTITY_PARTITION)
        return provided

    def register_steps(self, steps):
        for step in steps.itervalues():
            self.add_vertex(step.name, self.STEP_PARTITION)

            for in_ in step.ins:
                self.add_vertex(in_, self.ENTITY_PARTITION)
                self.add_edge(in_, step.name)
                self.entities.register_entity(in_)

            for out in step.outs:
                self.add_vertex(out, self.ENTITY_PARTITION)
                self.add_edge(step.name, out)
                self.entities.register_entity(out)

    def register_attribute(self, attributes):
        pass

    def provide_entity(self, entity):
        if entity.alias in self.provided_entities:
            raise ValueError('an entity with the alias {} is already provided'.format(entity.alias))
        self.provided_entities[entity.alias] = entity

    def update(self, other):
        super(Template, self).update(other)

        self.provided_entities.update(other.provided_entites)
        self.entities.update(other.entities)
        self.steps.update(other.steps)
        self.attributes.update(other.attributes)
        self.parser.update(other.parser)
