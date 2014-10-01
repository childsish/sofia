import os
import re

from ebias.provided_resource import ProvidedResource

class ResourceParser(object):
    """ A parser for resources on the command line and from resource files.
    
    The resource string takes the form of:
        -r <fname>[:type=<type>][:<name>][:<kwargs>]
    where
        <fname>
            is the file name of the resource
        <type>
            is the type of entity found in the resource
        <name>
            is an alternative name of the resource. This is used when
            referencing the resource in a feature string.
        <kwargs>
            are the arguments passed to a resource upon initialisation
    
    An example:
        -r /tmp/tmp.vcf:type=vcf:tmp
    """
    
    REGX = re.compile('^(?P<fname>(?:[\w]:)?[^:]+)' +\
                      '(?::(?P<part1>[^:]+))?' +\
                      '(?::(?P<part2>[^:]+))?' +\
                      '(?::(?P<part3>[^:]+))?$')
    
    def __init__(self, default_types):
        """ Initialise with default entity types based on file extension. """
        self.default_types = default_types
    
    def parseResources(self, resource_strings):
        """ Parse all resource strings in a list. """
        res = {}
        for resource_string in resource_strings:
            resource = self.parseResource(resource_string)
            res[resource.name] = resource
        return res
    
    def parseResource(self, resource_string):
        """ Parse a resource string. """
        match = self.REGX.match(resource_string)
        if match is None:
            raise ValueError('Unable to parse resource string: %s'%\
                resource_string)
        fname = match.group('fname')
        type = None
        name = None
        init_args = {}
        for part in match.groups()[1:]:
            if part is None:
                continue
            elif part.startswith('type='):
                if type is not None:
                    raise ValueError('Resource type specified multiple times')
                type = part[5:]
            elif '=' in part:
                if len(init_args) > 0:
                    raise ValueError('Resource initialisation arguments '\
                        'specified multiple times')
                init_args = dict(p.split('=') for p in part.split(','))
            else:
                if name is not None:
                    raise ValueError('Resource name specified multiple times')
                name = part
        return self.createResource(fname, type, name, init_args)
    
    def createResource(self, fname, type=None, name=None, init_args={}):
        """ Create a resource. """
        if fname.endswith('.gz'):
            ext = fname.rsplit('.', 2)[1]
        else:
            ext = fname.rsplit('.', 1)[1]
        if type is None and ext not in self.default_types:
            raise ValueError('Unable to determine type of biological information stored in %s'%fname)
        type = self.default_types[ext] if type is None else type
        name = os.path.basename(fname) if name is None else name
        return ProvidedResource(fname, type, name, init_args)
