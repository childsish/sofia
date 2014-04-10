import os
import re

from collections import OrderedDict
from common import loadPlugins, loadResource
from itertools import izip
from modules.feature import Feature
from modules.resource import Resource

def aggregate(args):
    program_dir = os.path.dirname(os.path.abspath(__file__))
    feature_dir = os.path.join(program_dir, 'features')
    feature_types = loadPlugins(feature_dir, Feature)
    resource_dir = os.path.join(program_dir, 'resources')
    resource_parsers = loadPlugins(resource_dir, Resource)
    
    requested_resources = {'target': args.input}
    requested_resources.update(args.resources)
    resources = loadResources(requested_resources, resource_parsers, args.formats)
    
    top_level_features = getTopLevelFeatures(args.features, feature_types, resources)
    features = generateDependencies(top_level_features, resources)
    
    print '\t'.join(features[name].name for name in args.features)
    for entity in resources['target']:
        entities = {'target': entity}
        cols = [features[name].generate(entities, features) for name in args.features]
        out = [ftr.format(col) for ftr, col in izip(args.features, cols)]
        print '\t'.join(out)

def loadResources(requested, parsers, formats):
    resources = {}
    for name, fname in requested.iteritems():
        resources[name] = loadResource(fname, parsers, formats.get(name, None))
    return resources
    
def getTopLevelFeatures(features, available, resources):
    """get the top level features
    
    Instantiates the top level features and makes sure that the resource maps
    all fully filled and don't reference undefined resources. If one resource
    remains undefined, then assume it refers to the target resource.
    
    :param list features: the feature string from the command line
    :param dict available: all features extensions
    :param dict resources: all defined resources
    """
    regx = re.compile('(?P<name>\w+)(:(?P<map>[\w=,]+))?')
    res = []
    for feature in features:
        match = regx.match(feature).groupdict()
        feature_class = available[match['name']]
        defined_resource_map = {} if match['map'] is None else\
            OrderedDict(m.split('=') for m in match['map'].split(','))
        
        resource_map = {}
        undefined = set()
        for resource in feature_class.RESOURCES:
            k = v = resource
            if k in defined_resource_map:
                v = defined_resource_map[k]
            if v not in resources:
                undefined.add((k, v))
            else:
                resource_map[k] = v
        if len(undefined) > 1:
            msg = 'Attempting to use undefined resources: %s'
            raise Exception(msg%','.join(v for k, v in undefined))
        elif len(undefined) == 1:
            k, v = undefined.pop()
            resource_map[k] = 'target'
        
        res.append(feature_class(resource_map))
    return res

def generateDependencies(features, resources):
    res = {feature.name: feature for feature in features}
    stk = features[:]
    while len(stk) > 0:
        parent = stk.pop(0)
        for feature in parent.generateDependencies(resources):
            res[feature.name] = feature
            stk.append(feature)
    return res
