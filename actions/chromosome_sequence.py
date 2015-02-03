from sofia_.action import Action


class GetHomopolymerLength(Action):
    """
    Count the number of downstream nucleotides that have the same identity at the given position.
    """
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['homopolymer_length']

    def init(self, max_length=100):
        self.max_length = max_length
    
    def calculate(self, variant, chromosome_sequence_set):
        res = []
        for alt in variant['alt'].split(','):
            indel = len(variant['ref']) != len(alt)
            pos = variant['genomic_position']['chromosome_pos'] + indel
            seq = chromosome_sequence_set.get_interval(variant['genomic_position']['chromosome_id'], pos, pos + self.max_length)
            
            ref = variant['ref'] if len(variant['ref']) >= len(alt) else alt
            i = 0
            while i < len(seq) and seq[i] == ref[indel]:
                i += 1
            res.append(i)
        return res
    
    def format(self, homopolymer_length):
        unq = set(homopolymer_length)
        if len(unq) == 1:
            return str(list(unq)[0])
        return ','.join(str(i) for i in homopolymer_length)
