import os

from ebias.resource import Resource, Target

from lhc.file_format.fasta_.set_ import FastaSet as FastaSetParser
from lhc.file_format.fasta_.iterator import FastaIterator as FastaIteratorParser
from lhc.file_format.fasta_.index import IndexedFastaFile

class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'chromosome_sequence'
    PARSER = FastaSetParser
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        fname = self.getFilename()
        self.parser = IndexedFastaFile(fname) if os.path.exists('%s.fai'%fname)\
            else FastaSetParser(FastaIteratorParser(fname))
