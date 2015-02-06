import argparse
import os
import pysam

from iterator import GffLineIterator, GffEntityIterator
from lhc.argparse import OpenReadableFile, OpenWritableFile
from lhc.io.bed import iter_bed


class IndexedGffFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)

        if not os.path.exists('{}.tbi'.format(self.fname)):
            raise ValueError('File missing interval index. Try: tabix -p gff <FILENAME>.')
        self.ivl_index = pysam.Tabixfile(self.fname)

        if not os.path.exists('{}.lci'.format(self.fname)):
            raise ValueError('File missing key index. Try: python -m lhc.io.gff index <FILENAME>')
        self.key_index = {entry.name: entry.ivl for entry in iter_bed('{}.lci'.format(self.fname))}

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.get_gene(key)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            l = len(key.ref) if hasattr(key, 'ref') else 1
            return self.get_genes_in_interval(key.chr, key.pos, key.pos + l)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.get_genes_in_interval(key.chr, key.start, key.stop)
        raise NotImplementedError('Random access not implemented for {}'.format(type(key)))

    def get_gene(self, gene_id, interval=None):
        interval = self.key_index[gene_id] if interval is None else interval
        lines = [GffLineIterator.parse_line(line)
                 for line in self.ivl_index.fetch(interval.chr, interval.start, interval.stop)]
        return GffEntityIterator.parse_gene([line for line in lines if line.attr['gene_name'] == gene_id])

    def get_genes_at_position(self, chr, pos):
        return self.get_genes_in_interval(chr, pos, pos + 1)

    def get_genes_in_interval(self, chr, start, stop):
        lines = [GffLineIterator.parse_line(line) for line in self.ivl_index.fetch(chr, start, stop)]
        return [self.get_gene(line.attr['gene_name'], line) for line in lines if line.type == 'gene']


def index(args):
    it = GffLineIterator(args.input)
    for line in (line for line in it if line.type == 'gene'):
        args.output.write('{}\t{}\t{}\t{}\t.\t{}\n'.format(line.chr, line.start, line.stop, line.attr['gene_name'],
                                                           line.strand))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys
    add_arg = parser.add_argument
    add_arg('-i', '--input', action=OpenReadableFile, default=sys.stdin,
            help='The gff file to index by gene name (default: stdin).')
    add_arg('-o', '--output', action=OpenWritableFile, default=sys.stdout,
            help='The file to write the output to in bed format (default: stdout).')
    parser.set_defaults(func=index)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
