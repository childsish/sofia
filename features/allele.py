from collections import Counter
from modules.feature import Feature
from resource import DynamicResource

class MinorAlleleFrequency(Feature):
    
    NAME = 'maf'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'locus',
         'feature': DynamicResource,
         'resource_map': {'name': 'locus'}
        }
    ]
    
    def calculate(self, locus):
        cnt = Counter()
        for v in locus.samples.itervalues():
            if v['GT'] == '.':
                continue
            a1, a2 = v['GT'].split('/')
            cnt[a1] += 1
            cnt[a2] += 1
        return min(cnt.itervalues()) / float(sum(cnt.itervalues()))

    def format(self, entity):
        return '%.03f'%entity

