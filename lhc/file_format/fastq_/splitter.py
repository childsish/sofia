import argparse

from iterator import FastqEntryIterator
from lhc.binf.alignment.local_aligner import LocalAligner
from lhc.file_format.fasta import FastaEntryIterator, FastaSet


class FastqBarcodeSplitter(object):
    def __init__(self, score, gap_penalty):
        self.aligner = LocalAligner(gap_penalty=gap_penalty)
        self.score = score

    def split(self, input_fastq, barcode_fname, out_dir):
        aligner = self.aligner
        barcodes = FastaSet(FastaEntryIterator(barcode_fname))
        score = self.score
        missing = 0
        out_fhndls = {}
        for entry in FastqEntryIterator(input_fastq):
            alignments = [(hdr, aligner.align(entry.seq, seq)) for hdr, seq in barcodes]
            hdr, alignment = sorted(alignments, key=lambda x: x[1].score)
            if alignment.score < score:
                missing += 1
                continue
            if hdr not in out_fhndls:
                out_fhndls[hdr] = open(os.path.join(out_dir, hdr), 'w')
            fhndl = out_fhndls[hdr]
            fhndl.write()


def split(args):
    splitter = FastqBarcodeSplitter(args.score, args.gap_penalty)
    splitter.split(args.input, args.barcodes)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys
    add_arg = parser.add_argument
    add_arg('input',
            help='The input fastq file to split')
    add_arg('barcodes',
            help='A fasta file of sequences')
    add_arg('-O', '--output',
            help='The output directory.')
    add_arg('-s', '--score', type=float,
            help='The minimum score to allow a match (default: length of the barcode).')
    add_arg('-p', '--penalty', type=int,
            help='The gap penalty (default: -10).')
    parser.set_defaults(func=split)
    return parser
