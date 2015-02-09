from sofia_.entity import Entity


class amino_acid_variant(Entity):
    """
    A protein variant.
    """

    CHILDREN = ['protein_position', 'ref', 'alt', 'indel', 'interval']

    def format(self, amino_acid_variant):
        res = []
        pos = amino_acid_variant.pos
        ref = amino_acid_variant.ref
        for alt, fs in zip(amino_acid_variant.alt, amino_acid_variant.fs):
            if len(amino_acid_variant.ref) > len(alt):
                d = len(amino_acid_variant.ref) - len(alt)
                rng = str(pos + len(ref) - 1,) if d == 1 else '{}_{}'.format(pos + len(ref) - d, pos + len(ref) - 1)
                r = 'p.{}del{}'.format(rng, ref[-d - 1:-1])
            elif len(alt) > len(amino_acid_variant.ref):
                d = len(alt) - len(amino_acid_variant.ref)
                typ = 'dup' if alt[-d - 1:-1] == ref[-d - 1:-1] else 'ins'
                rng = str(pos + len(alt) - 1,) if d == 1 else '{}_{}'.format(pos + len(alt) - d, pos + len(alt) - 1)
                r = 'p.{}{}{}'.format(rng, typ, alt[-d - 1:-1])
            else:
                i = 0
                j = len(ref) - 1
                if ref != alt:
                    while ref[i] == alt[i]:
                        i += 1
                    while ref[j] == alt[j]:
                        j -= 1
                    j += 1
                r = 'p.{}{}{}'.format(ref[i:j + 1], pos + i + 1, alt[i:j + 1])
                if fs is not None:
                    r += 'fs*{}'.format(fs)
            res.append(r)
        return ','.join(res)
