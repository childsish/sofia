import argparse
import cPickle
import os

from lhc.interval import Interval
from operator import add
from vcf_.merger import VcfMerger
from vcf_.iterator import VcfIterator
from vcf_.index import VcfFileIndexer

def iterEntries(fname):
    return VcfIterator(fname)

def index(fname, iname=None):
    if fname.endswith('.gz'):
        raise IOError('Unable to index compressed files.')
    
    indexer = VcfFileIndexer()
    ivl_index = indexer.index(fname)
    
    iname = '%s.idx'%fname if iname is None else iname
    outfile = open(iname, 'wb')
    cPickle.dump(fname, fhndl, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(ivl_index, outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def merge(fnames, quality=50.0, out=None):
    import sys
    
    out = sys.stdout if out is None else open(out, 'w')
    if len(fnames) == 1 and os.path.isdir(fnames[0]):
        fnames = [os.path.join(fnames[0], fname) for fname in os.listdir(fnames[0])]
    merger = VcfMerger(fnames, quality)
    for key, values in merger.hdrs.iteritems():
        for value in values:
            out.write('%s=%s\n'%(key, value))
    out.write('#CHR\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(merger.sample_names) + '\n')
    for entry in merger:
        out.write('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(\
            entry.chr,
            entry.pos + 1,
            entry.id,
            entry.ref,
            entry.alt,
            entry.qual,
            entry.filter,
            entry.info,
            ':'.join(entry.samples.values()[0].iterkeys()),
            '\t'.join(':'.join(sample.itervalues())\
                for sample in entry.samples.itervalues())
        ))
    out.close()

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('input', metavar='FILE')
    index_parser.add_argument('-o', '--output', metavar='FILE')
    index_parser.set_defaults(func=lambda args:index(args.input))
    
    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument('inputs', nargs='+', metavar='FILE')
    merge_parser.add_argument('-q', '--quality', type=float)
    merge_parser.add_argument('-o', '--output')
    merge_parser.set_defaults(func=lambda args: merge(args.inputs,
                                                      args.quality,
                                                      args.output))
    
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())

