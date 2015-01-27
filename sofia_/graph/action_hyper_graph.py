from hyper_graph import HyperGraph


class ActionHyperGraph(HyperGraph):
    """ A hyper graph of all the possible action calculation pathways. """
    def __init__(self, entity_graph):
        super(ActionHyperGraph, self).__init__()
        self.actions = dict()
        self.entity_graph = entity_graph

    @property
    def entities(self):
        return self.es

    def register_action(self, action):
        """ Add an action to the hyper graph.

        :param action: The action to add to the graph.
        """
        self.actions[action.name] = action

        for in_ in action.ins:
            self.add_inward_edge(action.name, in_)

        for out in action.outs:
            self.add_outward_edge(action.name, out)
