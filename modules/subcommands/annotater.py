class Annotater(object):
    def __init__(self, target_features, features, resources):
        self.target_features = target_features
        self.features = features
        self.resources = resources
    
    def annotate(self):
        print '\t'.join(self.features[name].name for name in self.target_features)
        for entity in self.resources['target']:
            entities = {}
            entities['target'] = entity
            for resource in self.resources:
                if resource != 'target':
                    entities[resource] = self.resources[resource][entity]
            res = [self.features[name].generate(entities, self.features)\
                for name in self.target_features]
            print '\t'.join(map(str, res))
