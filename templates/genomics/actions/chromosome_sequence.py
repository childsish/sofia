from sofia_.action import Action


class GetHomopolymer(Action):
    """
    Get the stretch of identical nucleotides at the variant
    """
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['homopolymer']

    def calculate(self, variant, chromosome_sequence_set):
        res = []
        for alt in variant['alt'].split(','):
            ref = variant['ref']
            i = 0
            while i < len(ref) and i < len(alt) and ref[i] == alt[i]:
                i += 1
            ref = ref[i:]
            alt = alt[i:]
            pos = variant['genomic_position']['chromosome_pos'] + i
            seq = chromosome_sequence_set.fetch(variant['genomic_position']['chromosome_id'], pos, pos + 100)
            
            i = 0
            while seq[i] == seq[0]:
                i += 1
            res.append(seq[:i])
        return res
