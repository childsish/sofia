from warnings import warn

from lhc.io.fasta import FastaEntryIterator, FastaSet, IndexedFastaSet
from lhc.io.fasta_.set_ import FastaSet

from sofia import Resource


class FastaChromosomeSequenceSet(Resource):
    
    EXT = {'.fasta', '.fasta.gz', '.fasta.bgz', '.fa', '.fa.gz'}
    FORMAT = 'fasta_file'
    OUT = ['chromosome_sequence_set']
    
    def get_interface(self, filename):
        try:
            import pysam
            return IndexedFastaSet(pysam.FastaFile(filename))
        except Exception, e:
            warn(e.message)
        warn('no index available for {}, loading whole file...'.format(filename))
        return FastaSet(FastaEntryIterator(filename))
