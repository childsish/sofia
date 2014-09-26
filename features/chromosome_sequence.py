from ebias.feature import Feature

class HomopolymerLength(Feature):
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['homopolymer_length']

    def init(self, max_length=100):
        self.max_length = max_length
    
    def calculate(self, variant, chromosome_sequence_set):
        res = []
        for alt in variant.alt.split(','):
            indel = len(variant.ref) != len(variant.alt)
            pos = variant.pos + indel
            seq = chromosome_sequence_set.getInterval(variant.chr, pos,
                pos + self.max_length)
            
            ref = variant.ref if len(variant.ref) >= len(variant.alt) else\
                variant.alt
            i = 0
            while i < len(seq) and seq[i] == ref[indel]:
                i += 1
            res.append(i)
        return res
    
    def format(self, homopolymer_length):
        return ','.join(str(i) for i in homopolymer_length)

