from collections import defaultdict
from modules.feature import Feature
from resource import DynamicResource, StaticResource
from lhc.binf.genetic_code import GeneticCodes

class AminoAcidMutation(Feature):
    
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
    DESCRIPTION = '''Calculate the amino acid mutation in the form
    <reference_amino_acid><protein_position><alternate_amino_acid>
    eg. K12V'''
    
    REVCMP = {'a': 't', 'c': 'g', 'g': 'c', 't': 'a',
              'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    
    def __init__(self, resource_map, resources=None):
        super(AAMut, self).__init__(resource_map, resources)
        self.gc = GeneticCodes()[1]
    
    def calculate(self, locus, mdl, seq):
        if len(locus.alt) > 1 or len(locus.ref) > 1:
            return  {}
        muts = {}
        for m in mdl:
            mdl_muts = defaultdict(set)
            for k, v in m.transcripts.iteritems():
                subseq = v.getSubSeq(seq, valid_types=set(['CDS']))
                if subseq == '':
                    continue
                try:
                    relpos = v.getRelPos(locus.pos)
                except IndexError:
                    continue
                cdnpos = relpos - relpos % 3
                cdn = list(subseq[cdnpos:cdnpos + 3])
                try:
                    fr = self.gc[''.join(cdn).lower()]
                except TypeError:
                    continue
                cdn[relpos % 3] = locus.alt if v.ivl.strand == '+' else self.REVCMP[locus.alt]
                to = self.gc[''.join(cdn).lower()]
                mut = '%s%s%s'%(fr, cdnpos / 3 + 1, to)
                mdl_muts[mut].add(k)
            if len(mdl_muts) == 1:
                muts[m.name] = mdl_muts.keys()[0]
            else:
                for k, vs in mdl_muts.iteritems():
                    for v in vs:
                        muts[v] = k
        return muts

    def format(self, entity):
        if len(entity) == 1:
            return entity.values()[0]
        return ','.join('%s:%s'%item for item in entity.iteritems())
