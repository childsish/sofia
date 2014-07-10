from ebias.resource_feature import ResourceFeature

from lhc.file_format.fasta_.set_ import FastaSet as FastaSetParser
from lhc.file_format.fasta_.iterator import FastaIterator as FastaIteratorParser

class FastaChromosomeSequenceSet(ResourceFeature):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'chromosome_sequence'
    PARSER = FastaSetParser
    OUT = ['chromosome_sequence_set']

class FastaCodingSequenceSet(ResourceFeature):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'coding_sequence'
    PARSER = FastaSetParser
    OUT = ['coding_sequence_set']

class FastaCodingSequenceIterator(ResourceFeature):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'coding_sequence'
    PARSER = FastaIteratorParser
    OUT = ['coding_sequence_iterator']

class FastaProteinSequenceSet(ResourceFeature):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'protein_sequence'
    PARSER = FastaSetParser
    OUT = ['protein_sequence_set']

class FastaProteinSequenceIterator(ResourceFeature):
    
    EXT = ['.fasta', '.fasta.gz']
    TYPE = 'protein_sequence'
    PARSER = FastaIteratorParser
    OUT = ['protein_sequence_iterator']
