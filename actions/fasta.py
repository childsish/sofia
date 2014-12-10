import os
import sys

from sofia_.action import Resource

from modules.file_formats.fasta import FastaSet as FastaSetParser, FastaIterator as FastaIteratorParser

class FastaChromosomeSequenceSet(Resource):
    
    EXT = ['.fasta', '.fasta.gz']
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
