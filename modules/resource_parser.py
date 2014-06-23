import os
import re

from modules.resource_wrapper import ResourceWrapper

class ResourceParser(object):
    """ -r <fname>[;type=<type>][;<name>]
        -r /tmp/tmp.vcf:tmp:type=vcf
    """
    
    REGX = re.compile('^(?P<fname>[^;]+)' +\
                      '(?:;type=(?P<type>\w+))?' +\
                      '(?:;(?P<name>\w+))?$')
    
    def __init__(self, parsers):
        self.parsers = parsers
    
    def parseResources(self, resources):
        res = []
        for resource in resources:
            match = self.REGX.match(resource)
            if match is None:
                raise ValueError('Unable to parse resource string: %s'%resource)
            res.append(self.parseResource(**match.groupdict()))
        return res
    
    def parseResource(self, fname, name=None, type=None):
        type = self.getType(fname) if type is None else type
        if type not in self.parsers:
            raise ValueError('No parsers exist for resource type "%s"'%type)
        parser = self.parsers[type](fname)
        return ResourceWrapper(parser,
            os.path.split(fname)[1] if name is None else name,
            out=[type])
    
    def parseTarget(self, fname, type=None):
        types = {'vcf': ['variant', 'genomic_position'], 'gtf': ['gene_model']}
        type = self.getType(fname) if type is None else type
        parser = self.parsers[type](fname)
        return ResourceWrapper(parser, 'target', out=types[type])
    
    def getType(self, fname):
        if not os.path.isdir(fname):
            parts = fname.split('.')
            if parts[-1] == 'gz':
                return parts[-2]
            return parts[-1]
        exts = set(f.rsplit('.', 1)[1] for f in os.listdir(fname))
        if len(exts) > 1:
            raise ValueError('Can not determine type of resource %s. Multiple types (file extensions) found in %s'%(name, fname))
        return 'multi' + list(exts)[0]
