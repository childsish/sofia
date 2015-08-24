from lhc.graph import HyperGraph


class Template(HyperGraph):
    """ A hyper graph of all the possible step calculation pathways. """
    def __init__(self, entity_graph):
        super(Template, self).__init__()
        self.steps = dict()
        self.entity_graph = entity_graph

    def __str__(self):
        """ Convert to string

        :return: A string representing the graph in Graphviz format.
        """
        res = ['digraph {} {{'.format(self.name)]
        for e, v in sorted(self.graph.es.iteritems()):
            res.append('    "{}" -> "{}";'.format(v.fr, v.to))
        for entity in self.entity_graph.entities.itervalues():
            if 'is_a' in entity:
                res.append('    "{}" -> "{}" [color=red,type=dotted,label="is_a"]'.format(entity['name'], entity['is_a']))
            if 'has_a' in entity:
                for has_a in entity['has_a']:
                    res.append('    "{}" -> "{}" [color=blue,type=dotted,label="has_a"]'.format(entity['name'], has_a))
        for v in sorted(self.vs):
            res.append('    "{}" [shape=box];'.format(v))
        res.append('}')
        return '\n'.join(res)

    @property
    def entities(self):
        return self.vs

    def register_entity(self, entity):
        self.add_vertex(entity)
        self.entity_graph.register_entity(entity)

    def register_step(self, step):
        """ Add an step to the hyper graph.

        :param step: The step to add to the graph.
        """
        self.steps[step.name] = step

        for in_ in step.ins:
            self.add_outward_edge(in_, step.name)
            self.register_entity(in_)

        for out in step.outs:
            self.add_inward_edge(out, step.name)
            self.register_entity(out)
