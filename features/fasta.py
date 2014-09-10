from ebias.resource import Resource, Target

from lhc.file_format.fasta_.set_ import FastaSet as FastaSetParser
from lhc.file_format.fasta_.iterator import FastaIterator as FastaIteratorParser
from lhc.file_format.fasta_.index import IndexedFastaFile

class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz', '.fasta.idx']
    TYPE = 'chromosome_sequence'
    PARSER = FastaSetParser
    OUT = ['chromosome_sequence_set']
    
    def init(self, **kwargs):
        fname = self.getFilename()
        self.parser = IndexedFastaFile(fname) if fname.endswith('.fasta.idx')\
            else FastaSetParser(FastaIteratorParser(fname))

class FastaCodingSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz', '.fasta.idx']
    TYPE = 'coding_sequence'
    PARSER = FastaSetParser
    OUT = ['coding_sequence_set']
    
    def init(self, **kwargs):
        fname = self.getFilename()
        self.parser = IndexedFastaFile(fname) if fname.endswith('.fasta.idx')\
            else FastaSetParser(FastaIteratorParser(fname))

class FastaCodingSequenceIterator(Target):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'coding_sequence'
    PARSER = FastaIteratorParser
    TARGET = True
    OUT = ['coding_sequence_iterator']

class FastaProteinSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz', '.fasta.idx']
    TYPE = 'protein_sequence'
    PARSER = FastaSetParser
    OUT = ['protein_sequence_set']
    
    def init(self, **kwargs):
        fname = self.getFilename()
        self.parser = IndexedFastaFile(fname) if fname.endswith('.fasta.idx')\
            else FastaSetParser(FastaIteratorParser(fname))

class FastaProteinSequenceIterator(Target):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'protein_sequence'
    PARSER = FastaIteratorParser
    TARGET = True
    OUT = ['protein_sequence_iterator']

