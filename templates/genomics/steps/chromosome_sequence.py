from sofia.step import Step


class GetHomopolymer(Step):
    """
    Get the stretch of identical nucleotides at the variant
    """
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['homopolymer']

    def run(self, variant, chromosome_sequence_set):
        ref = variant.ref
        alt = variant.alt
        i = 0
        while i < len(ref) and i < len(alt) and ref[i] == alt[i]:
            i += 1
        pos = variant.pos + i
        seq = chromosome_sequence_set.fetch(variant.chr, pos, pos + 100)

        i = 0
        while i < len(seq) and seq[i] == seq[0]:
            i += 1
        yield seq[:i]
