def quality(qua, offset=33):
    return [ord(char) - offset for char in qua]

def iterFastq(fname):
    infile = open(fname)
    try:
        while True:
            yield (infile.next().strip(),
                infile.next().strip(),
                infile.next().strip(),
                infile.next().strip())
    except StopIteration:
        pass
    infile.close()

def removeDuplicates(infname, outfname=None):
    def meanQuality(v):
        return mean(quality(v[2]))
        
    from collections import defaultdict
    from numpy import mean
    
    if outfname is None:
        outfname = '%s.unq.fastq'%infname.rsplit('.', 1)[1]
    visited = defaultdict(list)
    for hdr, seq, plus, qua in iterFastq(infname):
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

def main(argv):
    def rmdup(args):
        return removeDuplicates(args.input, args.output)
    
    import argparse
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    parser_rmdup = subparsers.add_parser('rmdup')
    parser_rmdup.add_argument('input')
    parser_rmdup.add_argument('output', nargs='?', default=None)
    parser_rmdup.set_defaults(func=rmdup)
    
    args = parser.parse_args(argv[1:])
    args.func(args)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
