from sofia_.action import Resource
from modules.file_formats.fasta_.iterator import FastaIterator as FastaIteratorParser
from modules.file_formats.fasta_.set_ import FastaSet as FastaSetParser
try:
    from modules.file_formats.fasta_.index import IndexedFastaFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Fasta file access will be slower.')
    IndexedFastaFile = lambda fname: FastaSetParser(FastaIteratorParser(fname))


class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        self.parser = IndexedFastaFile(self.getFilename())
