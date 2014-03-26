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
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    annotate_parser = subparsers.add_parser('annotate')
    annotate_parser.add_argument('input', metavar='N', nargs='+',
        help='the VCF files to annotate')
    annotate_parser.add_argument('-f', '--features', nargs='+') # ftr1:key1=res1 ftr2:key2=res2
    annotate_parser.add_argument('-r', '--resources', nargs='+', action=MakeDict, default={})
    annotate_parser.add_argument('-t', '--types', nargs='+', action=MakeDict, default={})
    annotate_parser.set_defaults(func=annotate)
    
    index_parser = subparsers.add_parser('index')
    index_parser.set_defaults(func=index)
    
    joiner_parser = subparsers.add_parser('join')
    joiner_parser.add_argument('input')
    joiner_parser.set_defaults(func=join)
    
    return parser

def annotate(args):
    def parseFeatures(features, available):
        regx = re.compile('(?P<name>\w+)(=(?P<header>\w+))?(:(?P<map>[\w=,]+))?')
        res = []
        for ftr_str in features:
            match = regx.match(ftr_str).groupdict()
            match['map'] = {} if match['map'] is None else\
                OrderedDict(m.split('=') for m in match['map'].split(','))
            
            feature = available[match['name']](match['map'])
            res.append(feature)
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
    
    from modules.subcommands.annotater import Annotater
    
    program_dir = os.path.dirname(os.path.abspath(__file__))
    feature_dir = os.path.join(program_dir, 'features')
    available = loadPlugins(feature_dir, Feature)
    
    parser_dir = os.path.join(program_dir, 'resources')
    parsers = loadPlugins(parser_dir, Resource)
    
    args.input = args.input[0] if len(args.input) == 1 else join(args)
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
    
    features = parseFeatures(args.features, available)
    features = generateDependencies(features, resources)
    
    annotater = Annotater(args.features, features, resources)
    annotater.annotate()

def index(args):
    pass

def join(args):
    
    from subcommands.joiner import Joiner
    
    base = os.path.dirname(args.output)
    input = map(os.path.basename, args.input)
    fname = os.path.join(base, os.path.commonprefix(input) + '.vcf')
    
    if len(args.input) == 1:
        import shutil
        shutil.copy(args.input[0], fname)
    
    joiner = Joiner()
    joiner.join(args.input)

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
