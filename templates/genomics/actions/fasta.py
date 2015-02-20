import os

from sofia_.action import Resource
from lhc.io.fasta_.index import IndexedFastaSet
from lhc.io.fasta_.iterator import FastaEntryIterator
from lhc.io.fasta_.set_ import FastaSet
from warnings import warn


class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                import pysam
                self.parser = IndexedFastaSet(pysam.TabixFile(fname))
                return
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(fname)):
            from lhc.io.txt_ import index
            self.parser = IndexedFastaSet(index.IndexedFile(fname))
            return
        warn('no index available for {}, loading whole file...'.format(fname))
        self.parser = FastaSet(FastaEntryIterator(fname))
