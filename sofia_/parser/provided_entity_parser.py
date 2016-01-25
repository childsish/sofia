import os

from sofia_.entity import Entity


class ResourceParser(object):
    """ A parser for resources on the command line and from resource files.
    
    The resource string takes the form of:
        <provided_resource> ::= <resource>[:<name>][:<attribute>[:<attribute>]*]
        <attribute> ::= <key>=<value>[,<value>]*
    where
        resource
            is the file name of the resource
        <name>
            is an alternative name of the resource. This is used when
            referencing the resource in a requested entity.
        <key>
            is the name of an attribute
        <value>
            is the value of an attribute
    
    An example:
        -r /tmp/tmp.vcf
        -r "/tmp/tmp.vcf:tmp:format=vcf"
        -r "tmp.vcf:tmp:format=vcf:x=x:y=y:chromosome_id=ucsc"
    """

    def __init__(self, extensions):
        self.extensions = extensions
    
    def parse_resources(self, resource_strings):
        """ Parse all resource strings in a list. """
        res = {}
        for resource_string in resource_strings:
            resource = self.parse_resource(resource_string)
            res[resource.alias] = resource
        return res
    
    def parse_resource(self, resource_string):
        """ Parse a single provided resource.

        :param resource_string: definition of provided resource
        :return: ProvidedResource
        """
        parts = resource_string.split(':')
        filename = parts[0]
        alias = None
        attributes = {'filename': filename}
        for part in parts[1:]:
            if '=' in part:
                k, v = part.split('=', 1)
                attributes[k] = v.split(',')[0] #TODO: allow multiple values
            else:
                alias = part

        name = None
        for key, value in self.extensions.iteritems():
            if filename.endswith(key):
                name = value
        if name is None:
            name = attributes.pop('entity', None)
        if name is None:
            raise ValueError('Resource {} has unknown entity'.format(filename))
        if alias is None:
            alias = os.path.basename(filename)
        resources = {alias}
        return Entity(name, resources, attributes, alias)
