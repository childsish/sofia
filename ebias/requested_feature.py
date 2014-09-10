class RequestedFeature(object):
    def __init__(self, name, resources=[], args={}):
        self.name = name
        self.resources = resources
        self.args = args
    
    def __str__(self):
        res = [self.name]
        if len(self.args) > 0:
            res.append('%s=%s'%e for e in sorted(self.args.iteritems()))
        if len(self.resources) > 0:
            res.append(','.join(self.resources))
        return ':'.join(res)

    def __eq__(self, other):
        return str(self) == str(other)

