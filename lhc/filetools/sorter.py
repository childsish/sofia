import argparse
import bz2
import json
import os

from lhc.argparse import OpenReadableFile, OpenWritableFile
from lhc.file_format.txt import TypedColumnExtractor
from lhc.itertools.chunked_iterator import ChunkedIterator
from lhc.itertools.sorted_iterator_merger import SortedIteratorMerger


def main():
    args = get_parser().parse_args()
    if args.tmp_dir is None:
        import tempfile
        args.tmp_dir = tempfile.mkdtemp()
    fhndl = TypedColumnExtractor(args.input, args.columns, args.sep)
    fnames = sort(fhndl, args.tmp_dir, args.max_lines)
    fname = merge(fnames, args.tmp_dir, args.max_handles)
    index = compress(fname, args.output, args.block_size)
    fhndl = open(args.output, 'w')
    json.dump(index, fhndl)
    fhndl.close()


def sort(fhndl, tmp_dir, max_lines=2 ** 16):
    fnames = []
    it = ChunkedIterator(fhndl, max_lines)
    for i, lines in enumerate(it):
        lines = sorted(lines, key=interval_as_key)
        out_fname = '{}.vcf.gz'.format(i)
        out_fhndl = open(os.path.join(tmp_dir, out_fname), 'w')
        for line in lines:
            if line is None:
                continue
            out_fhndl.write(line)
        out_fhndl.close()
        fnames.append(out_fname)
    return fnames


def merge(fnames, tmp_dir, max_handles=2 ** 8):
    i = 0
    while len(fnames) > 1:
        it = ChunkedIterator(fnames, max_handles)
        new_fnames = []
        for j, chunk_fnames in enumerate(it):
            fname = '{}_{}.vcf.gz'.format(i, j)
            new_fnames.append(fname)
            out_fhndl = open(os.path.join(tmp_dir, fname), 'w')
            merger = SortedIteratorMerger([VcfLineIterator(fname) for fname in chunk_fnames], key=interval_as_key)
            for line in merger:
                out_fhndl.write('{}\n'.format(line))
            out_fhndl.close()
        fnames = new_fnames
        i += 1
    return fnames[0]


def compress(in_fname, out_fname, compression_level=1):
    block_size = compression_level * 100000
    index = {'block_sze': block_size, 'blocks': []}
    in_fhndl = open(in_fname)
    out_fhndl = bz2.BZ2File(out_fname, 'w', compressionlevel=compression_level)

    ttl = 0
    for line in in_fhndl:
        if ttl + len(line) > block_size:
            out_fhndl.write((block_size - ttl) * ' ')
            index['blocks'].append({'chr': None, 'fr': None, 'to': None})
            ttl = 0
        out_fhndl.write(line)
        ttl += len(line)
        if line.startswith('#CHROM'):
            break

    prv_chr = None
    prv_pos = 0
    for line in in_fhndl:
        chr = line[:line.find('\t')]
        if chr != prv_chr or ttl + len(line) > block_size:
            out_fhndl.write((block_size - ttl) * ' ')
            chr, pos, discard = line.split('\t', 2)
            pos = int(pos) - 1
            index['blocks'].append({'chr': prv_chr, 'fr': prv_pos, 'to': pos})
            prv_pos = 0 if chr != prv_chr else pos
            prv_chr = chr
            ttl = 0
        out_fhndl.write(line)
        ttl += len(line)
    in_fhndl.close()
    out_fhndl.close()
    return index


def interval_as_key(interval):
    return interval.chr, interval.pos, interval.pos + len(interval.ref)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('output',
            help='The name of the output file.')
    add_arg('columns', default='s1', narg='+',
            help='The columns in sort order. 1-indexed.')
    add_arg('-c', '--compression-level', default=9,
            help="The compression level of the output file (1-9; 100's of kB).")
    add_arg('-f', '--max_handles', default=2 ** 8,
            help='The maximum number of file handles to open.')
    add_arg('-i', '--input', action=OpenReadableFile, default=sys.stdin,
            help='The name of the input vcf file (default: stdin).')
    add_arg('-l', '--max-lines', default=2 ** 16,
            help='The maximum number of input lines to read at a time.')
    add_arg('-t', '--tmp-dir',
            help='The directory where temporary files are stored.')
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
