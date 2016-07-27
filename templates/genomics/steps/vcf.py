import gzip

from lhc.io.vcf import VcfEntryIterator
from lhc.filetools import SharedFile
from sofia.step import Step, EndOfStream


class IterateVcf(Step):

    IN = ['vcf_file']
    OUT = ['variant']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins) > 0:
            if self.iterator is None:
                vcf_file = ins.vcf_file.pop()
                if vcf_file is EndOfStream:
                    outs.variant.push(EndOfStream)
                    return True
                fileobj = gzip.open(vcf_file) if vcf_file.endswith('.gz') else SharedFile(vcf_file)
                self.iterator = VcfEntryIterator(fileobj)

            for item in self.iterator:
                if not outs.variant.push(item):
                    return False
            self.iterator = None
        return len(ins) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'variant': set()
        }
