import os

from sofia_.step import Resource
from lhc.io.fasta_.index import IndexedFastaSet
from lhc.io.fasta_.iterator import FastaEntryIterator
from lhc.io.fasta_.set_ import FastaSet
from warnings import warn


class FastaChromosomeSequenceSet(Resource):
    
    EXT = {'.fasta', '.fasta.gz', '.fasta.bgz'}
    FORMAT = 'fasta'
    OUT = ['chromosome_sequence_set']
    
    def get_interface(self, filename):
        if os.path.exists('{}.fai'.format(filename)):
            try:
                from lhc.io.fasta_.pysam_ import PysamFastaSet
                return PysamFastaSet(filename)
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(filename)):
            return IndexedFastaSet(filename)
        warn('no index available for {}, loading whole file...'.format(filename))
        return FastaSet(FastaEntryIterator(filename))
