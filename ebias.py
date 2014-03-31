#!/usr/bin/env python
import argparse
import os
import re

from collections import OrderedDict
from modules.feature import Feature
from modules.resource import Resource

def main(argv):
    parser = getParser()
    args = parser.parse_args()
    aggregate(args)

def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='TARGET',
        help='the VCF files to annotate')
    parser.add_argument('features', nargs='+',
        help='features take the form <feature_name>[:<resource_key>[=<resource_name>]]') # ftr1:key1=res1 ftr2:key2=res2
    parser.add_argument('-r', '--resources', nargs='*', action=MakeDict, default={})
    parser.add_argument('-t', '--types', nargs='*', action=MakeDict, default={})
    return parser

def aggregate(args):
    from modules.subcommands.annotater import Annotater
    
    prog_dir = os.path.dirname(os.path.abspath(__file__))
    ftr_dir = os.path.join(prog_dir, 'features')
    ftr_clss = loadPlugins(ftr_dir, Feature)
    res_dir = os.path.join(prog_dir, 'resources')
    res_clss = loadPlugins(res_dir, Resource)
    
    req_ress = {'target': args.input}
    req_ress.update(args.resources)
    ress = loadResources(req_ress, res_clss, args.types)
    
    top_level_features = instantiateTopLevelFeatures(args.features, ftr_clss, ress)
    ftrs = generateDependencies(top_level_features, ress)
    
    annotater = Annotater([ftr.name for ftr in top_level_features], ftrs, ress)
    annotater.annotate()

def loadResources(req_ress, res_clss, types):
    ress = {}
    for name, fname in req_ress.iteritems():
        ress[name] = loadResource(name, fname, res_clss, types)
    return ress

def loadResource(name, fname, res_clss, types):
    if name in types:
        return res_clss[types[name]](fname)
    for res_cls in res_clss:
        if fname.endswith(res_cls):
            return res_clss[res_cls](fname)
    raise TypeError('Unrecognised file format: %s'%\
        os.path.basename(fname))
    
def instantiateTopLevelFeatures(features, available, resources):
    """Instantiate the top level features
    
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

def loadPlugins(indir, cls):
    sys.path.append(indir)
    plugins = {}

    mnames = (fname[:-3] for fname in os.listdir(indir)\
        if fname[0] != '.' and fname.endswith('.py'))

    for mname in mnames:
        d = __import__(mname).__dict__
        for k, v in d.iteritems():
            if k == cls.__name__:
                continue
            try:
                if issubclass(v, cls):
                    plugins[v.NAME] = v
            except TypeError:
                continue
    return plugins

class MakeDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, OrderedDict(v.split('=') for v in values))

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
