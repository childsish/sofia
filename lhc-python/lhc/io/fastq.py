import argparse
import sys

from fastq_.iterator import FastqEntryIterator
from fastq_ import split
from lhc.argparse import OpenReadableFile, OpenWritableFile


def iter_entries(fname):
    for entry in FastqEntryIterator(fname):
        yield entry


def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    parser_rmdup = subparsers.add_parser('rmdup')
    parser_rmdup.add_argument('input')
    parser_rmdup.add_argument('output', nargs='?', default=None)
    parser_rmdup.set_defaults(func=lambda args:rmdup(args.input, args.output))
    
    parser_interleave = subparsers.add_parser('interleave')
    parser_interleave.add_argument('fastq1')
    parser_interleave.add_argument('fastq2')
    parser_interleave.set_defaults(\
        func=lambda args:interleave(args.fastq1, args.fastq2))

    parser_split = subparsers.add_parser('split')
    split.define_parser(parser_split)
    
    parser_to_fasta = subparsers.add_parser('to_fasta')
    parser_to_fasta.add_argument('-i', '--input', default=sys.stdin, action=OpenReadableFile,
                                help='Input fastq file (default: stdin).')
    parser_to_fasta.add_argument('-o', '--output', default=sys.stdout, action=OpenWritableFile,
                                help='Output fasta file (default: stdout).')
    parser_to_fasta.set_defaults(func=lambda args: to_fasta(FastqEntryIterator(args.input), args.output))
    
    args = parser.parse_args(argv[1:])
    args.func(args)


def rmdup(infname, outfname=None):
    def meanQuality(v):
        return mean(quality(v[2]))
        
    from collections import defaultdict
    from numpy import mean
    
    if outfname is None:
        outfname = '%s.unq.fastq'%infname.rsplit('.', 1)[1]
    visited = defaultdict(list)
    for hdr, seq, plus, qua in iter_entries(infname):
        visited[seq].append((hdr, seq, qua))
    print visited.values()[0]
    outfile = open(outfname, 'w')
    for hdr, seq, qua in sorted(visited.itervalues(), key=meanQuality):
        outfile.write(hdr)
        outfile.write('\n')
        outfile.write(seq)
        outfile.write('\n+\n')
        outfile.write(qua)
        outfile.write('\n')
    outfile.close()


def quality(qua, offset=33):
    return [ord(char) - offset for char in qua]


def interleave(fastq1, fastq2, outfile=sys.stdout):
    infile1 = open(fastq1)
    infile2 = open(fastq2)

    try:
        while True:
            for i in xrange(4):
                outfile.write(infile1.next())
            for i in xrange(4):
                outfile.write(infile2.next())
    except StopIteration:
        pass

    infile1.close()
    infile2.close()

def to_fasta(in_fhndl, out_fhndl):
    for entry in in_fhndl:
        out_fhndl.write('>{}\n{}\n'.format(entry.hdr, entry.seq))


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

