from lhc.io.vcf import VcfEntryIterator
from sofia.step import Step, EndOfStream


class IterateVcf(Step):

    IN = ['vcf_file', 'filepool']
    OUT = ['variant']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins.vcf_file) > 0:
            if self.iterator is None:
                vcf_file = ins.vcf_file.pop()
                if vcf_file is EndOfStream:
                    outs.variant.push(EndOfStream)
                    return True
                filepool = ins.filepool.peek()
                self.iterator = VcfEntryIterator(filepool.open(vcf_file))

            for item in self.iterator:
                if not outs.variant.push(item):
                    return False
            self.iterator = None
        return len(ins.vcf_file) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename,
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'variant': set()
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'variant': ins['vcf_file']
        }
