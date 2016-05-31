from __future__ import with_statement

import gzip

from sofia.step import Step
from lhc.io.fasta.iterator import FastaIterator
from lhc.io.fasta.inorder_access_set import FastaInOrderAccessSet


class FastaChromosomeSequenceSet(Step):

    IN = ['fasta_file']
    OUT = ['chromosome_sequence_set']
    
    def run(self, fasta_file):
        with gzip.open(fasta_file) if fasta_file.endswith('.gz') else open(fasta_file) as fileobj:
            yield FastaInOrderAccessSet(iter(FastaIterator(fileobj)))

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'chromosome_sequence_set': set()
        }
