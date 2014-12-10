from sofia_.action import Resource
from modules.file_formats.fasta import FastaSet as FastaSetParser, FastaIterator as FastaIteratorParser
try:
    from modules.file_formats.fasta import IndexedFastaFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Fasta file access will be slower.')
    IndexedFastaFile = lambda fname: FastaSetParser(FastaIteratorParser(fname))


class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        self.parser = IndexedFastaFile(self.getFilename())
