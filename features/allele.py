from collections import Counter
from modules.feature import Feature
from resource import DynamicResource

class AlleleCount(Feature):

    NAME = 'allele_count'
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
        return cnt

class MinorAlleleFrequency(Feature):
    
    NAME = 'maf'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'allele_count',
         'feature': AlleleCount,
         'resource_map': {'locus': 'locus'}
        }
    ]
    
    def calculate(self, allele_count):
        return min(allele_count.itervalues()) / float(sum(allele_count.itervalues()))

    def format(self, entity):
        return '%.03f'%entity

class MinorAlleleCount(Feature):
    
    NAME = 'mac'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'allele_count',
         'feature': AlleleCount,
         'resource_map': {'locus': 'locus'}
        }
    ]

    def calculate(self, allele_count):
        return min(allele_count.itervalues())
    
