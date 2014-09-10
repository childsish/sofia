class RequestedFeature(object):
    def __init__(self, name, requested_resources=[], args={}):
        self.name = name
        self.requested_resources = requested_resources
        self.args = args
    
    def __str__(self):
        res = [self.name]
        if len(self.args) > 0:
            res.append('%s=%s'%e for e in sorted(self.args.iteritems()))
        if len(self.requested_resources) > 0:
            res.append(','.join(self.requested_resources))
        return ':'.join(res)

    def __eq__(self, other):
        return str(self) == str(other)

