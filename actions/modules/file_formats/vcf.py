import argparse
import glob
import sys

from vcf_.index import IndexedVcfFile
from vcf_.iterator import VcfIterator
from vcf_.merger import VcfMerger
from vcf_.set_ import VcfSet


def iter_entries(fname):
    return VcfIterator(fname)


def merge(glob_fnames, quality=50.0, out=None, bams=[]):
    fnames = []
    for glob_fname in glob_fnames:
        fname = glob.glob(glob_fname)
        if len(fname) == 0:
            raise ValueError('%s does not match any existing files' % glob_fname)
        fnames.extend(fname)
    out = sys.stdout if out is None else open(out, 'w')
    merger = VcfMerger(fnames, quality, bams=bams)
    for key, values in merger.hdrs.iteritems():
        for value in values:
            out.write('%s=%s\n' % (key, value))
    out.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(merger.sample_names) + '\n')
    for entry in merger:
        format = sorted(key for key in entry.samples.itervalues().next().keys() if key != '.')
        out.write('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
            entry.chr,
            entry.pos + 1,
            entry.id,
            entry.ref,
            entry.alt,
            entry.qual,
            entry.filter,
            entry.info,
            ':'.join(format),
            '\t'.join('.' if '.' in entry.samples[sample] else
                      ':'.join(entry.samples[sample][f] for f in format)
                      for sample in merger.sample_names)
        ))
    out.close()


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument('inputs', nargs='+', metavar='FILE')
    merge_parser.add_argument('-b', '--bams', nargs='+')
    merge_parser.add_argument('-q', '--quality', type=float)
    merge_parser.add_argument('-o', '--output')
    merge_parser.set_defaults(func=lambda args: merge(args.inputs, args.quality, args.output, args.bams))

    return parser


if __name__ == '__main__':
    sys.exit(main())
