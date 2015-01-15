import argparse
import itertools
import multiprocessing
import os
import sys

from iterator import FastqEntryIterator
from lhc.argparse import OpenReadableFile
from lhc.binf.sequence import revcmp
from lhc.file_format.fasta import FastaEntryIterator
from lhc.string import hamming


def split(args):
    if args.output is None:
        args.output = args.input.rsplit('.fastq', 1)[0]

    forward_barcodes_ = [(hdr, seq.lower(), get_seeds(seq.lower(), args.seed_size))
                         for hdr, seq in FastaEntryIterator(args.barcodes)]
    reverse_barcodes_ = [(hdr, revcmp(seq.lower()), get_seeds(revcmp(seq.lower()), args.seed_size))
                         for hdr, seq in FastaEntryIterator(args.barcodes)]
    initargs = [forward_barcodes_, reverse_barcodes_, args.max_mismatch]
    pool = multiprocessing.Pool(args.cpus, initializer=init_worker, initargs=initargs)

    if hasattr(args, 'reverse_reads'):
        split_paired(args.forward_reads, args.reverse_reads, pool, args.output, args.simultaneous_entries)
    else:
        split_single(args.forward_reads, pool, args.output, args.simultaneous_entries)


def split_single(reads, pool, output, simultaneous_entries):
    pool_iterator = FastqEntryIterator(reads)
    iterator = FastqEntryIterator(reads)
    out_fhndls = {}
    for hdrs, entry in itertools.izip(pool.imap(find_barcodes_single, pool_iterator, simultaneous_entries), iterator):
        for hdr in hdrs:
            if hdr not in out_fhndls:
                fname = '{}.fastq'.format(hdr)
                out_fhndls[hdr] = open(os.path.join(output, fname), 'w')
            out_fhndls[hdr].write(str(entry))
    for out_fhndl in out_fhndls.itervalues():
        out_fhndl.close()


def split_paired(forward, reverse, pool, output, simultaneous_entries):
    pool_iterator = itertools.izip(FastqEntryIterator(forward), FastqEntryIterator(reverse))
    forward_iterator = FastqEntryIterator(forward)
    reverse_iterator = FastqEntryIterator(reverse)
    out_fhndls = {}
    it = itertools.izip(pool.imap(find_barcodes_paired, pool_iterator, simultaneous_entries),
                        forward_iterator,
                        reverse_iterator)
    for hdrs, forward_entry, reverse_entry in it:
        for hdr in hdrs:
            if hdr not in out_fhndls:
                forward_fname = '{}.1.fastq'.format(hdr)
                reverse_fname = '{}.2.fastq'.format(hdr)
                forward_file = open(os.path.join(output, forward_fname), 'w')
                reverse_file = open(os.path.join(output, reverse_fname), 'w')
                out_fhndls[hdr] = (forward_file, reverse_file)
            out_fhndls[hdr][0].write(str(forward_entry))
            out_fhndls[hdr][1].write(str(reverse_entry))
    for out_fhndls in out_fhndls.itervalues():
        out_fhndls[0].close()
        out_fhndls[1].close()
 

def get_seeds(s, k):
    return [s[i:i + k] for i in xrange(len(s) - k)]

mismatch = 0
forward_barcodes = None
reverse_barcodes = None


def init_worker(forward_barcodes_, reverse_barcodes_, mismatch_=0):
    global mismatch
    global forward_barcodes
    global reverse_barcodes
    
    mismatch = mismatch_
    forward_barcodes = forward_barcodes_
    reverse_barcodes = reverse_barcodes_


def find_barcodes_single(entry):
    forward_hdrs = find_barcodes(entry, forward_barcodes)
    reverse_hdrs = find_barcodes(entry, reverse_barcodes)
    return forward_hdrs + reverse_hdrs


def find_barcodes_paired(entries):
    forward, reverse = entries
    forward_hdrs = find_barcodes(forward, forward_barcodes)
    reverse_hdrs = find_barcodes(reverse, reverse_barcodes)
    return forward_hdrs + reverse_hdrs


def find_barcodes(entry, barcodes):
    template = entry.seq.lower()

    ## String find
    if mismatch == 0:
        return [hdr for hdr, barcode, seeds in barcodes if template.find(barcode) >= 0]

    ## Hamming with seed
    hdrs = []
    for hdr, barcode, seeds in barcodes:
        for i, seed in enumerate(seeds):
            try:
                idx = template.index(seed)
                d = hamming(template[idx - i:idx - i + len(barcode)], barcode)
                if d <= mismatch:
                    hdrs.append(hdr) 
            except ValueError:
                pass
    return hdrs
 

def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('forward_reads',
            help='Fastq containing forward reads.')
    add_arg('reverse_reads', nargs='?',
            help='Fastq containing reverse reads (optional).')
    add_arg('barcodes',
            help='Fasta file of barcode sequences')
    add_arg('-c', '--cpus',
            help='The number of cpus to use (default: all).')
    add_arg('-k', '--seed-size', default=5,
            help='The size of the seed (default: 5).')
    add_arg('-m', '--max-mismatch', type=float, default=0,
            help='The number of allowed mismatched (default: 1).')
    add_arg('-s', '--simultaneous-entries', default=1000,
            help='The number of entries to submit to each worker at a time (default: 1000).')
    add_arg('-O', '--output',
            help='The output directory.')
    parser.set_defaults(func=split)
    return parser

if __name__ == '__main__':
    sys.exit(main())
