from sofia_.action import Resource
from lhc.io.fasta_.iterator import FastaEntryIterator as FastaIteratorParser
from lhc.io.fasta_.set_ import FastaSet as FastaSetParser
try:
    from lhc.io.fasta_.index import IndexedFastaFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Fasta file access will be slower.\n')
    IndexedFastaFile = lambda fname: FastaSetParser(FastaIteratorParser(fname))


class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        self.parser = IndexedFastaFile(self.get_filename())
