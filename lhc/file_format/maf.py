import argparse
import os

from lhc.filepool import FilePool
from lhc.binf.variant import Variant
from lhc.binf.genomic_coordinate import Interval

CHR = 4
START = 5
STOP = 6
TYPE = 9
REF = 10
ALT1 = 11
ALT2 = 12
GENOTYPE = 15

def iterMaf(fname):
    infile = open(fname)
    infile.readline()
    for line in infile:
        parts = line.split('\t')
        yield Variant(Interval(parts[CHR], int(parts[START]) - 1, int(parts[STOP])),
            [parts[ALT1], parts[ALT2]], [parts[TYPE], parts[TYPE]],
            0.0, parts[GENOTYPE])
    infile.close()

def main(argv):
    parser = argparse.ArgumentParser(description='Mutation Annotation File functions')
    subparsers = parser.add_subparsers(help='sub-command help')
    
    split_parser = subparsers.add_parser('split', help='Split MAF help')
    split_parser.add_argument('input_file', help='The MAF file to split')
    split_parser.add_argument('-o', '--output_directory', help='The directory to place the output')
    split_parser.set_defaults(func=lambda args:splitMaf(args.input_file, args.output_directory))
    
    args = parser.parse_args(argv[1:])
    args.func(args)
    
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
        
        genotype_id = line.split('\t')[GENOTYPE]
        key = os.path.join(outdir, genotype_id + '.maf')
        if key not in file_pool:
            file_pool[key].write(hdr)
        file_pool[key].write(line)
    file_pool.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
