class Annotater(object):
    def __init__(self, target_features, features, resources):
        self.target_features = target_features
        self.features = features
        self.resources = resources
    
    def annotate(self):
        print self.target_features
        print self.features
        print '\t'.join(self.features[name].name for name in self.target_features)
        for entity in self.resources['target']:
            entities = {}
            entities['target'] = entity
            res = [self.features[name].generate(entities, self.features)\
                for name in self.target_features]
            print '\t'.join(map(str, res))
