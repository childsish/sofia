import os
import argparse

from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.filepool import FilePool
from lhc.binf.genomic_coordinate import Interval

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

def splitMaf(fname, outdir=None):
    if outdir is None:
        outdir = fname.rsplit('.', 1)[0]
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    infile = open(fname)
    file_pool = FilePool('w')
    for line in infile:
        if line[0] == '#':
            continue
        
        genotype_id = line.split('\t')[15]
        file_pool[os.path.join(outdir, genotype_id + '.maf')].write(line)
    file_pool.close()

def iterMaf(fname):
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', 4)
    column_builder.registerColumn('fr', 5, int)
    column_builder.registerColumn('to', 6, int)
    column_builder.registerColumn('strand', 7)
    column_builder.registerColumn('type', 9)
    column_builder.registerColumn('ref', 10)
    column_builder.registerColumn('alt1', 11)
    column_builder.registerColumn('alt2', 12)
    column_builder.registerColumn('genotype_id', 15)
    
    field_builder = FieldBuilder()
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('type')
    field_builder.registerField('ref')
    field_builder.registerField('alt1')
    field_builder.registerField('alt2')
    field_builder.registerField('genotype_id')
    
    for fields in iterCsv(fname, column_builder, field_builder, skip=1):
        yield fields

def parseInterval(cols):
    return Interval(cols.chr, cols.fr - 1, cols.to, cols.strand)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
