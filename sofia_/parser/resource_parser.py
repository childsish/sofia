import argparse

from argument_dictionary import ArgumentDictionary
from provided_resource import ProvidedResource


class ResourceParser(object):
    """ A parser for resources on the command line and from resource files.
    
    The resource string takes the form of:
        -r "[-n NAME] [-t TYPE] [-p PARAM] [-a ATTR] resource"
    where
        resource
            is the file name of the resource
        NAME
            is an alternative name of the resource. This is used when
            referencing the resource in an step string.
        FORMAT
            is the file format of the resource
        PARAM
            are the arguments passed to a resource upon initialisation
        ATTR
            are the attributes of the resource
    
    An example:
        -r /tmp/tmp.vcf
        -r "/tmp/tmp.vcf -n tmp -t vcf"
        -r "tmp.vcf -n tmp -t vcf -k x=x y=y -a chromosome_id=ucsc"
    """
    
    def __init__(self):
        """ Initialise with default entity types based on file extension. """
        self.parser = self._define_parser()
    
    def parse_resources(self, resource_strings):
        """ Parse all resource strings in a list. """
        res = {}
        for resource_string in resource_strings:
            resource = self.parse_resource(resource_string)
            res[resource.name] = resource
        return res
    
    def parse_resource(self, resource_string):
        """ Parse a resource string. """
        args = self.parser.parse_args(resource_string.split())
        return ProvidedResource(args.resource, args.format, args.name, args.param, args.attr, args.ins, args.outs)
    
    def _define_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('resource')
        parser.add_argument('-n', '--name')
        parser.add_argument('-f', '--format')
        parser.add_argument('-p', '--param', action=ArgumentDictionary, nargs='+', default={})
        parser.add_argument('-a', '--attr', action=ArgumentDictionary, nargs='+', default={})
        parser.add_argument('-i', '--ins', nargs='+', default=[])
        parser.add_argument('-o', '--outs', nargs='+')
        return parser
