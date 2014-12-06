class RequestedAction(object):
    """ An action that the user requests. """
    def __init__(self, name, resources=set(), param={}, attr={}):
        self.name = name
        self.resources = resources
        self.param = param
        self.attr = attr
    
    def __str__(self):
        res = [self.name]
        if len(self.param) > 0:
            res.append(','.join('%s=%s'%e for e in sorted(self.param.iteritems())))
        if len(self.resources) > 0:
            res.append(','.join(r.name for r in self.resources))
        return ':'.join(res)

    def __eq__(self, other):
        return str(self) == str(other)
