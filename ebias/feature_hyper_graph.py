from collections import defaultdict
from itertools import product, izip
from operator import or_

from lhc.graph.hyper_graph import HyperGraph
from error_manager import ERROR_MANAGER
from feature_graph import FeatureGraph
from feature_wrapper import FeatureWrapper
from features import Resource, Target, Extractor, Converter
from solution_iterator import SolutionIterator

class FeatureHyperGraph(object):
    """ A hyper graph of all the possible feature calculation pathways. """
    def __init__(self, entity_graph):
        self.outs = defaultdict(set)
        self.ins = defaultdict(set)
        self.features = {}
        self.graph = HyperGraph()
        self.entity_graph = entity_graph
    
    def __str__(self):
        """ Returns a dot formatted representation of the graph. """
        return str(self.graph)
    
    @property
    def vs(self):
        return self.graph.vs

    def registerFeature(self, feature):
        """ Add a feature to the hyper graph. """
        def getEntityName(entity):
            return ''.join(part.capitalize() for part in entity.split('_')).replace('*', '')
        
        c_feature = feature.name
        self.features[c_feature] = feature
        self.graph.addVertex(c_feature)
        
        for in_ in feature.ins:
            self.ins[in_].add(c_feature)
            self.graph.addEdge(in_, c_feature)
            for in_origin in self.outs[in_]:
                self.graph.addEdge(in_, c_feature, in_origin)
            for in_, out in ((path[0], path[-1]) for path in self.entity_graph.getAncestorPaths(in_) if len(path) == 2):
                extractor_name = 'Extract%sFrom%s'%\
                        (getEntityName(out), getEntityName(in_))
                extractor = FeatureWrapper(Extractor,
                    extractor_name,
                    ins={in_: self.entity_graph.createEntity(in_)},
                    outs={out: self.entity_graph.createEntity(out)},
                    param={'path': [in_, out]},
                    attr={'path': [in_, out]})
                self.features[extractor_name] = extractor
                self.graph.addVertex(extractor_name)
                self.graph.addEdge(in_, extractor_name)
                self.ins[in_].add(extractor_name)
                for in_origin in self.outs[in_]:
                    self.graph.addEdge(in_, extractor_name, in_origin)
                self.outs[out].add(extractor_name)
                for out_destination in self.ins[out]:
                    self.graph.addEdge(out, out_destination, extractor_name)

        for out in feature.outs:
            self.outs[out].add(c_feature)
            for out_destination in self.ins[out]:
                self.graph.addEdge(out, out_destination, c_feature)
        
        if feature.feature_class is not Converter and\
                issubclass(feature.feature_class, Converter):
            convertee = list(set(feature.ins) & set(feature.outs))[0]
            id_map = list(set(feature.ins) - set(feature.outs))[0]
            for path in self.entity_graph.getAncestorPaths(convertee):
                converter_name = 'Convert%sIn%s'%\
                        (getEntityName(path[-1]), getEntityName(path[0]))
                converter = FeatureWrapper(feature.feature_class,
                    converter_name,
                    ins=[path[0], id_map],
                    outs={path[0]: self.entity_graph.createEntity(path[0])},
                    attr={'path': path, 'map': id_map})
                self.features[converter_name] = converter
                self.graph.addVertex(converter_name)
                self.graph.addEdge(path[0], converter_name)
                for in_ in converter.ins:
                    self.ins[in_].add(converter_name)
                    for in_origin in self.outs[in_]:
                        self.graph.addEdge(in_, converter_name, in_origin)
                self.outs[path[0]].add(converter_name)
                for out_destination in self.ins[path[0]]:
                    self.graph.addEdge(path[0], out_destination, converter_name)
