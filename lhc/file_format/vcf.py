import argparse
import cPickle
import os

from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.interval import Interval
from operator import add
from vcf_.merger import VcfMerger
from vcf_.parser import VcfParser

def iterEntries(fname):
    parser = VcfParser(fname)
    return iter(parser)

def index(fname, iname=None):
    iname = VcfParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    pos_index, ivl_index = _createIndices(fname)
    cPickle.dump(pos_index, outfile, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(ivl_index, outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createIndices(fname):
    pos_index = Index((ExactKeyIndex, ExactKeyIndex))
    ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
    infile = open(fname, 'rb')
    chr = None
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.strip() == '' or line.startswith('#'):
            continue
        entry = VcfParser._parseUnsampledLine(line)
        pos_index[(entry.chr, entry.pos)] = fpos
        ivl = Interval(entry.pos, entry.pos + len(entry.ref))
        ivl_index[(entry.chr, ivl)] = fpos
        if entry.chr != chr:
            print entry.chr
            chr = entry.chr
    infile.close()
    return pos_index, ivl_index

def merge(fnames, quality=50.0):
    if len(fnames) == 1 and os.path.isdir(fnames[0]):
        fnames = [os.path.join(fnames[0], fname) for fname in os.listdir(fnames[0])]
    merger = VcfMerger(fnames, quality)
    for key, values in merger.hdrs.iteritems():
        for value in values:
            print '%s=%s'%(key, value)
    print '#CHR\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(merger.sample_names)
    for entry in merger:
        print '%s\t%s\t%s'%('\t'.join(map(str, entry[:-1])),
            ':'.join(entry.samples.values()[0].iterkeys()),
            '\t'.join(':'.join(sample.itervalues())\
                for sample in entry.samples.itervalues()))

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('input')
    index_parser.set_defaults(func=lambda args:index(args.input))
    
    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument('inputs', nargs='+')
    merge_parser.add_argument('-q', '--quality', type=float)
    merge_parser.set_defaults(func=lambda args: merge(args.inputs,
                                                      args.quality))
    
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
