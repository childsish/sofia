import gzip

from sofia.step import Resource
from lhc.io.fasta.iterator import FastaIterator
from lhc.io.fasta.inorder_access_set import FastaInOrderAccessSet


class FastaChromosomeSequenceSet(Resource):
    
    EXT = {'.fasta', '.fasta.gz', '.fasta.bgz', '.fa', '.fa.gz'}
    FORMAT = 'fasta_file'
    OUT = ['chromosome_sequence_set']
    
    def get_interface(self, filename):
        fileobj = gzip.open(filename) if filename.endswith('.gz') else open(filename)
        return FastaInOrderAccessSet(iter(FastaIterator(fileobj)))
