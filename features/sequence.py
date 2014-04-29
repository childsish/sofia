from modules.feature import Feature
from resource import StaticResource, DynamicResource

class Sequence(Feature):
    
    NAME = 'seq'
    RESOURCES = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'mdl',
         'feature': DynamicResource,
         'resource_map': {'name': 'mdl'}
        },
        {'name': 'seq',
         'feature': StaticResource,
         'resource_map': {'name': 'seq'}
        }
    ]
    
    def calculate(self, mdl, seq):
        res = {}
        for m in mdl:
            for k, v in m.transcripts.iteritems():
                res[k] = v.getSubSeq(seq, valid_types=set(['CDS']))
        return res
    
    def format(self, entity):
        if len(entity) == 0:
            return ''
        return str(entity)

