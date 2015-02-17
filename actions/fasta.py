from sofia_.action import Resource
try:
    from pysam import FastaFile as IndexedFastaSet
except ImportError:
    from lhc.io.fasta_.index import IndexedFastaSet


class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
    OUT = ['chromosome_sequence_set']
    
    def init(self):
        self.parser = IndexedFastaSet(self.get_filename())
