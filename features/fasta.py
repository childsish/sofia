import os
import sys

from ebias.features import Resource

from lhc.file_format.fasta_.set_ import FastaSet as FastaSetParser
from lhc.file_format.fasta_.iterator import FastaIterator as FastaIteratorParser

class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'chromosome_sequence'
    PARSER = FastaSetParser
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        fname = self.getFilename()
        if os.path.exists('%s.fai'%fname):
            try:
                from lhc.file_format.fasta_.index import IndexedFastaFile
                self.parser = IndexedFastaFile(fname)
                return
            except ImportError:
                sys.stderr.write('Pysam not available. Parsing entire file.')
                pass
        self.parser = FastaSetParser(FastaIteratorParser(fname))

