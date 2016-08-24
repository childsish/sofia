from lhc.io.vcf.iterator import Variant
from lhc.io.maf import MafIterator
from sofia.step import Step, EndOfStream


class IterateMaf(Step):

    IN = ['maf_file', 'filepool']
    OUT = ['maf']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins) > 0:
            if self.iterator is None:
                maf_file = ins.maf_file.pop()
                if maf_file is EndOfStream:
                    outs.maf.push(EndOfStream)
                    return True
                filepool = ins.filepool.peek()
                self.iterator = MafIterator(filepool.open(maf_file))

            for item in self.iterator:
                if not outs.maf.push(item):
                    return False
            self.iterator = None
        return len(ins) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename,
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'maf': set()
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'maf': ins['maf_file']
        }


class GetMafByVariant(Step):

    IN = ['variant', 'maf']
    OUT = ['maf']

    def __init__(self):
        self.variant = None
        self.mafs = []

    def run(self, ins, outs):
        variant = self.variant
        mafs = self.mafs

        while len(ins.variant) > 0 and len(ins.maf) > 0:
            if variant is None:
                variant = ins.variant.pop()
            if variant is EndOfStream:
                outs.maf.push(EndOfStream)
                return True

            i = 0
            while i < len(mafs) and mafs[i] < variant:
                i += 1
            del mafs[:i]

            while variant is not None and len(ins.maf) > 0:
                maf = ins.maf.peek()
                if maf is EndOfStream:
                    outs.maf.push(mafs, EndOfStream)
                    return True

                if maf > variant:
                    if not outs.maf.push(mafs):
                        self.variant = None
                        return False
                    variant = None
                elif maf == variant:
                    mafs.append(ins.maf.pop())
        self.variant = variant


class ConvertMafToVariant(Step):

    IN = ['maf']
    OUT = ['variant']

    def run(self, ins, outs):
        while len(ins) > 0:
            maf = ins.maf.pop()
            if maf is EndOfStream:
                outs.variant.push(EndOfStream)

            variant = Variant(maf.chromosome,
                              maf.start_position,
                              '.', maf.reference_allele,
                              ','.join({maf.tumour_seq_allele1, maf.tumour_seq_allele2} - {maf.reference_allele}),
                              maf.score,
                              '.')
            if not outs.variant.push(variant):
                break
        return len(ins) == 0
