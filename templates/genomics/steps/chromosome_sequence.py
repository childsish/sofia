from sofia_.step import Step


class GetHomopolymer(Step):
    """
    Get the stretch of identical nucleotides at the variant
    """
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['homopolymer']

    def calculate(self, variant, chromosome_sequence_set):
        res = []
        for alt in variant.alt.split(','):
            ref = variant.ref
            i = 0
            while i < len(ref) and i < len(alt) and ref[i] == alt[i]:
                i += 1
            pos = variant.pos + i
            seq = chromosome_sequence_set.fetch(variant.chr, pos, pos + 100)
            
            i = 0
            while seq[i] == seq[0]:
                i += 1
            res.append(seq[:i])
        return res
