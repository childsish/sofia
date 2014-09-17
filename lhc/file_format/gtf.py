import argparse
import gzip

from lhc.file_format.gtf_.iterator import GtfIterator

def iterEntries(fname):
    """ Convenience function """
    return GtfIterator(fname)

def index(fname):
    """ Query a gtf file by model name. Use tabix for interval queries. """
    index = []
    fhndl = gzip.open(fname) if fname.endswith('.gz') else open(fname)
    for line in fhndl:
        entry = GtfIterator._parseLine(line)
        index.append('%s\t%s\t%d\t%d'%(entry.attr['gene_name'], entry.chr, entry.start + 1, entry.stop + 1))
    fhndl.close()
    
    iname = '%s.lhci'%fname
    fhndl = open(iname)
    fhndl.write('\n'.join(index))
    fhndl.close()

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
