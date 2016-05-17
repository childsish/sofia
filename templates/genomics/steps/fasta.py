from __future__ import with_statement

import gzip

from sofia.step import Step
from lhc.io.fasta.iterator import FastaIterator
from lhc.io.fasta.inorder_access_set import FastaInOrderAccessSet


class FastaChromosomeSequenceSet(Step):

    IN = ['fasta_file']
    OUT = ['chromosome_sequence_set']
    
    def get_interface(self, filename):
        with gzip.open(filename) if filename.endswith('.gz') else open(filename) as fileobj:
            yield FastaInOrderAccessSet(iter(FastaIterator(fileobj)))
