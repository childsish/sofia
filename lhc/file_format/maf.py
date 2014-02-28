import os
import argparse

from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.filepool import FilePool
from lhc.tools import enum
from lhc.binf.genomic_coordinate import Interval, Position

def main(argv):
    def splitMafWrapper(args):
        splitMaf(args.input_file, args.output_directory)
    
    parser = argparse.ArgumentParser(description='Mutation Annotation File functions')
    subparsers = parser.add_subparsers(help='sub-command help')
    
    split_parser = subparsers.add_parser('split', help='Split MAF help')
    split_parser.add_argument('input_file', help='The MAF file to split')
    split_parser.add_argument('-o', '--output_directory', help='The directory to place the output')
    split_parser.set_defaults(func=splitMafWrapper)
    
    args = parser.parse_args(argv[1:])
    args.func(args)

VARIANT_TYPE = enum(['VARIANT', 'SNP'])

class MafParser(object):

    CHR = 4
    POS = 5
    FR = 5
    TO = 6
    STRAND = 7
    TYPE = 9
    REF = 10
    ALT1 = 11
    ALT2 = 12
    GENOTYPE = 15

    def __init__(self, type=VARIANT_TYPE.VARIANT):
        self.type = type

        self.column_builder = ColumnBuilder()
        self.column_builder.registerColumn('chr', MafParser.CHR)
        self.column_builder.registerColumn('fr', MafParser.FR, int)
        self.column_builder.registerColumn('to', MafParser.TO, int)
        self.column_builder.registerColumn('strand', MafParser.STRAND)
        self.column_builder.registerColumn('type', MafParser.TYPE)
        self.column_builder.registerColumn('ref', MafParser.REF)
        self.column_builder.registerColumn('alt1', MafParser.ALT1)
        self.column_builder.registerColumn('alt2', MafParser.ALT2)
        self.column_builder.registerColumn('genotype_id', MafParser.GENOTYPE)

        #TODO: Find a better place
        self.field_builder = FieldBuilder()
        self.field_builder.registerField('ivl', self._parseInterval)
        self.field_builder.registerField('type')
        self.field_builder.registerField('ref')
        self.field_builder.registerField('alt1')
        self.field_builder.registerField('alt2')
        self.field_builder.registerField('genotype_id')
        
        if type == VARIANT_TYPE.SNP:
            self.snp_field_builder = FieldBuilder()
            self.snp_field_builder.registerField('pos', self._parsePosition)
            self.snp_field_builder.registerField('ref')
            self.snp_field_builder.registerField('alt1')
            self.snp_field_builder.registerField('alt2')
            self.snp_field_builder.registerField('genotype_id')
    
    def iterFile(self, fname, skip=1):
        it = iterCsv(fname, self.column_builder, self.field_builder, skip)
        if self.type == VARIANT_TYPE.VARIANT:
            for row in it:
                yield row
        
        for row in it:
            if row.type == 'SNP':
                pos = Position(row.ivl.chr, row.ivl.start, row.ivl.strand)
                yield self.snp_field_builder.tuple._make([pos, row.ref,
                    row.alt1, row.alt2, row.genotype_id])
            elif row.type == 'DNP':
                for i in xrange(len(row.ref)):
                    pos = Position(row.ivl.chr, row.ivl.start + i,
                        row.ivl.strand)
                    yield self.snp_field_builder.tuple._make([pos, row.ref[i],
                        row.alt1[i], row.alt2[i], row.genotype_id])
            elif row.type in ('DEL', 'INS'):
                continue
            else:
                raise ValueError('Unrecognised variant type: %s'%row.type)
    
    def _parseInterval(self, cols):
        return Interval(cols.chr, cols.fr - 1, cols.to, cols.strand)
    
    def _parsePosition(self, cols):
        return Position(cols.chr, cols.fr - 1, cols.strand)
    
def splitMaf(fname, outdir=None):
    if outdir is None:
        outdir = fname.rsplit('.', 1)[0]
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    infile = open(fname)
    hdr = infile.readline()
    file_pool = FilePool('w')
    for line in infile:
        if line[0] == '#':
            continue
        
        genotype_id = line.split('\t')[15]
        key = os.path.join(outdir, genotype_id + '.maf')
        if key not in file_pool:
            file_pool[key].write(hdr)
        file_pool[key].write(line)
    file_pool.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
