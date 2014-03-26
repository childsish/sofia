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
    parser.add_argument('-f', '--features', nargs='*',
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
    
    args.resources['target'] = args.input
    
    resources = {}
    for name, fname in args.resources.iteritems():
        if name in args.types:
            resources[name] = parsers[args.types[name]](fname)
        else:
            for parser in parsers:
                if fname.endswith(parser):
                    resources[name] = parsers[parser](fname)
            if name not in resources:
                raise TypeError('Unrecognised file format: %s'%\
                    os.path.basename(fname))
    
    features = instantiateFeatures(args.features, available)
    features = generateDependencies(features, resources)
    
    annotater = Annotater(args.features, features, resources)
    annotater.annotate()
    
def instantiateFeatures(features, available):
    regx = re.compile('(?P<name>\w+)(=(?P<header>\w+))?(:(?P<map>[\w=,]+))?')
    res = []
    for ftr_str in features:
        match = regx.match(ftr_str).groupdict()
        feature_class = available[match['name']]
        resource_map = {res:res for res in feature_class.RESOURCES}
        match['map'] = {} if match['map'] is None else\
            OrderedDict(m.split('=') for m in match['map'].split(','))
        resource_map.update(match['map'])
        res.append(feature_class(resource_map))
    return res

def generateDependencies(features, resources):
    res = {feature.name: feature for feature in features}
    stk = features[:]
    while len(stk) > 0:
        parent = stk.pop()
        for dep in parent.DEPENDENCIES:
            resource_map = {k:parent.resource_map[v]\
                for k,v in dep['resource_map'].iteritems()}
            feature = dep['feature'](resource_map, resources)
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
