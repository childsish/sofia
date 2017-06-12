from sofia.step import Step


class GetHomopolymer(Step):
    """
    Get the stretch of identical nucleotides at the variant
    """
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['homopolymer']

    def consume_input(self, input):
        copy = {
            'variant': input['variant'][:],
            'chromosome_sequence_set': input['chromosome_sequence_set'][0]
        }
        del input['variant'][:]
        return copy

    def run(self, variant, chromosome_sequence_set):
        for variant_ in variant:
            ref = variant_.data['ref']
            alt = variant_.data['alt']
            i = 0
            while i < len(ref) and i < len(alt) and ref[i] == alt[i]:
                i += 1
            pos = variant_.position + i
            seq = chromosome_sequence_set.fetch(str(variant_.chromosome), pos, pos + 100)

            i = 0
            while i < len(seq) and seq[i] == seq[0]:
                i += 1
            yield seq[:i]

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'homopolymer': ins['variant']
        }
