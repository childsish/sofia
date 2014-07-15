import os
import re

from ebias.provided_resource import ProvidedResource

class ResourceParser(object):
    """ -r <fname>[;type=<type>][;<name>]
        -r /tmp/tmp.vcf;type=vcf;tmp
    """
    
    REGX = re.compile('^(?P<fname>[^;]+)' +\
                      '(?:;type=(?P<type>\w+))?' +\
                      '(?:;(?P<name>\w+))?$')
    
    def __init__(self, default_types):
        self.default_types = default_types
    
    def parseResources(self, resources):
        res = {}
        for resource in resources:
            match = self.REGX.match(resource)
            if match is None:
                raise ValueError('Unable to parse resource string: %s'%resource)
            resource = self.createResource(**match.groupdict())
            res[resource.name] = resource
        return res
    
    def createResource(self, fname, type=None, name=None):
        tmp_name, ext = fname.rsplit('.', 2)[:2] if fname.endswith('.gz') else fname.rsplit('.', 1)[:2]
        if type is None and ext not in self.default_types:
            raise ValueError('Unable to determine type of biological information stored in %s'%fname)
        type = self.default_types[ext] if type is None else type
        name = tmp_name if name is None else name
        return ProvidedResource(fname, type, name)
