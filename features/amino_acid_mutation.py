from modules.feature import Feature
from resource import DynamicResource, StaticResource
from lhc.binf.genetic_code import GeneticCodes

class Gene(Feature):
    
    NAME = 'aa_mut'
    RESOURCES = ['locus', 'mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'locus',
         'feature': DynamicResource,
         'resource_map': {'name': 'locus'}
        },
        {'name': 'mdl',
         'feature': DynamicResource,
         'resource_map': {'name': 'mdl'}
        },
        {'name': 'seq',
         'feature': StaticResource,
         'resource_map': {'name': 'seq'}
        }
    ]
    
    def calculate(self, locus, mdl, seq):
        gcode = GeneticCodes()[1]
        transcripts = {}
        for m in mdl:
            for k, v in m.transcripts.iteritems():
                try:
                    subseq = seq[v.ivl]
                    if subseq == '':
                        continue
                    transcripts[k] = (v.getRelPos(locus.pos), subseq)
                except IndexError:
                    pass
        res = {}
        for name, (relpos, subseq) in transcripts.iteritems():
            if len(locus.alt) > 1 or len(locus.ref) > 1:
                continue
            cdnpos = relpos - relpos % 3
            cdn = list(subseq[cdnpos:cdnpos + 3])
            fr = gcode[''.join(cdn).lower()]
            cdn[relpos % 3] = locus.alt
            to = gcode[''.join(cdn).lower()]
            res[name] = '%s%s%s'%(fr, cdnpos, to)
        return res

    def format(self, entity):
        if len(entity) == 1:
            return entity.values()[0]
        return ','.join('%s:%s'%item for item in entity.iteritems())
