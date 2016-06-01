from lhc.graph import NPartiteGraph


class Template(NPartiteGraph):

    ENTITY_PARTITION = 0
    STEP_PARTITION = 1

    """ A hyper graph of all the possible step calculation pathways. """
    def __init__(self, entity_graph):
        super(Template, self).__init__()
        self.steps = dict()
        self.entity_graph = entity_graph
        self.attributes = []

    def __str__(self):
        """ Convert to string

        :return: A string representing the graph in Graphviz format.
        """
        res = ['digraph {} {{'.format(self.name)]
        for entity in sorted(self.partitions[self.ENTITY_PARTITION]):
            res.append('    "{}" [shape=box];'.format(entity))
        for e, v in sorted(self.graph.es.iteritems()):
            res.append('    "{}" -> "{}";'.format(v.fr, v.to))
        for entity in self.entity_graph.entities.itervalues():
            if 'is_a' in entity:
                res.append('    "{}" -> "{}" [color=red,type=dotted,label="is_a"]'.format(entity['name'], entity['is_a']))
            if 'has_a' in entity:
                for has_a in entity['has_a']:
                    res.append('    "{}" -> "{}" [color=blue,type=dotted,label="has_a"]'.format(entity['name'], has_a))
        res.append('}')
        return '\n'.join(res)

    @property
    def entities(self):
        return self.partitions[self.ENTITY_PARTITION]

    def register_entity(self, entity):
        self.add_vertex(entity, self.ENTITY_PARTITION)
        self.entity_graph.register_entity(entity)

    def register_step(self, step):
        """ Add an step to the hyper graph.

        :param step: The step to add to the graph.
        """
        self.steps[step.name] = step
        self.add_vertex(step.name, self.STEP_PARTITION)

        for in_ in step.ins:
            self.add_vertex(in_, self.ENTITY_PARTITION)
            self.add_edge(in_, step.name)
            self.register_entity(in_)

        for out in step.outs:
            self.add_vertex(out, self.ENTITY_PARTITION)
            self.add_edge(step.name, out)
            self.register_entity(out)

    def register_attribute(self, attribute):
        self.attributes.append(attribute)
