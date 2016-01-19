from provided_resource import ProvidedResource


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
    
    def parse_resources(self, resource_strings):
        """ Parse all resource strings in a list. """
        res = {}
        for resource_string in resource_strings:
            resource = self.parse_resource(resource_string)
            res[resource.name] = resource
        return res
    
    def parse_resource(self, resource_string):
        """ Parse a single provided resource.

        :param resource_string: definition of provided resource
        :return: ProvidedResource
        """
        parts = resource_string.split(':')
        resource = parts[0]
        name = None
        attributes = {}
        for part in parts[1:]:
            if '=' in part:
                k, v = part.split('=', 1)
                attributes[k] = v.split(',')[0] #TODO: allow multiple values
            else:
                name = part
        format = attributes.pop('format', None)
        return ProvidedResource(resource, format, name, attributes)
