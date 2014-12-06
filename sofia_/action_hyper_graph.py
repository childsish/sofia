from collections import defaultdict

from lhc.graph.hyper_graph import HyperGraph
from action_wrapper import ActionWrapper
from action import Extractor

class ActionHyperGraph(object):
    """ A hyper graph of all the possible action calculation pathways. """
    def __init__(self, entity_graph):
        self.outs = defaultdict(set)
        self.ins = defaultdict(set)
        self.actions = {}
        self.graph = HyperGraph()
        self.entity_graph = entity_graph
    
    def __str__(self):
        """ Returns a dot formatted representation of the graph. """
        return str(self.graph)
    
    @property
    def vs(self):
        return self.graph.vs

    def registerAction(self, action):
        """ Add a action to the hyper graph. """
        def getEntityName(entity):
            return ''.join(part.capitalize() for part in entity.split('_')).replace('*', '')
        
        c_action = action.name
        self.actions[c_action] = action
        self.graph.addVertex(c_action)
        
        for in_ in action.ins:
            self.ins[in_].add(c_action)
            self.graph.addEdge(in_, c_action)
            for in_origin in self.outs[in_]:
                self.graph.addEdge(in_, c_action, in_origin)
            for in_, out in ((path[0], path[-1]) for path in self.entity_graph.getAncestorPaths(in_) if len(path) == 2):
                extractor_name = 'Extract%sFrom%s'%\
                        (getEntityName(out), getEntityName(in_))
                extractor = ActionWrapper(Extractor,
                    extractor_name,
                    ins={in_: self.entity_graph.createEntity(in_)},
                    outs={out: self.entity_graph.createEntity(out)},
                    param={'path': [in_, out]})
                self.actions[extractor_name] = extractor
                self.graph.addVertex(extractor_name)
                self.graph.addEdge(in_, extractor_name)
                self.ins[in_].add(extractor_name)
                for in_origin in self.outs[in_]:
                    self.graph.addEdge(in_, extractor_name, in_origin)
                self.outs[out].add(extractor_name)
                for out_destination in self.ins[out]:
                    self.graph.addEdge(out, out_destination, extractor_name)

        for out in action.outs:
            self.outs[out].add(c_action)
            for out_destination in self.ins[out]:
                self.graph.addEdge(out, out_destination, c_action)
