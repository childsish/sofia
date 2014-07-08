from ebias.resource import ResourceSet, ResourceIterator

from lhc.file_format.fasta_.set_ import FastaSet
from lhc.file_format.fasta_.iterator import FastaIterator

class FastaChromosomeSequenceSet(ResourceSet):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'chromosome_sequence'
    PARSER = FastaSet
    OUT = ['chromosome_sequence_set']

class FastaCodingSequenceSet(ResourceSet):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'coding_sequence'
    PARSER = FastaSet
    OUT = ['coding_sequence_set']

class FastaCodingSequenceIterator(ResourceIterator):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'coding_sequence'
    PARSER = FastaIterator
    OUT = ['coding_sequence_iterator']

class FastaProteinSequenceSet(ResourceSet):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'protein_sequence'
    PARSER = FastaSet
    OUT = ['protein_sequence_set']

class FastaProteinSequenceIterator(ResourceIterator):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'protein_sequence'
    PARSER = FastaIterator
    OUT = ['protein_sequence_iterator']
