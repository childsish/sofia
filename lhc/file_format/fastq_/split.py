import argparse
import multiprocessing
import os
import sys

from iterator import FastqEntryIterator
from lhc.argparse import OpenReadableFile
from lhc.binf.alignment.local_aligner import LocalAligner
from lhc.binf.sequence import revcmp
from lhc.file_format.fasta import FastaEntryIterator


def split(args):
    barcodes_ = [(hdr, seq.lower(), args.min_score if args.min_score else len(seq) - 1)
                 for hdr, seq in FastaEntryIterator(args.barcodes)]
    barcodes_.extend((hdr, revcmp(seq.lower()), score) for hdr, seq, score in barcodes_)
    pool = multiprocessing.Pool(initializer=init_worker, initargs=[barcodes_, args.gap_penalty])
    out_fhndls = {}
    iterator = FastqEntryIterator(args.input)
    for hdr, entry in pool.imap(find_barcode, iterator, 1000):
        if hdr not in out_fhndls:
            fname = '{}.fastq'.format(hdr)
            out_fhndls[hdr] = open(os.path.join(args.output, fname), 'w')
    for out_fhndl in out_fhndls.itervalues():
        out_fhndl.close()

aligner = None
barcodes = None


def init_worker(barcodes_, gap_penalty):
    global aligner
    global barcodes

    aligner = LocalAligner(gap_penalty=gap_penalty)
    barcodes = barcodes_


def find_barcode(entry):
    alignments = [(aligner.align(entry.seq.lower(), seq).score, hdr, min_score)
                  for hdr, seq, min_score in barcodes]
    score, hdr, min_score = sorted(alignments)[-1]
    if score >= min_score:
        hdr = 'None'
    return hdr, entry


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.output is None:
        if args.input is sys.stdin:
            parser.error('--output must be defined if --input not given.')
        args.output = args.input.rsplit(',', 2)[0]
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('barcodes',
            help='A fasta file of sequences')
    add_arg('-i', '--input', default=sys.stdin, action=OpenReadableFile,
            help='The input fastq file to split (default: stdin)')
    add_arg('-O', '--output',
            help='The output directory.')
    add_arg('-s', '--min-score', type=float,
            help='The minimum score to allow a match (default: length of the barcode).')
    add_arg('-p', '--gap-penalty', type=int,
            help='The gap penalty (default: -10).')
    parser.set_defaults(func=split)
    return parser

if __name__ == '__main__':
    sys.exit(main())
