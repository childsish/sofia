__author__ = 'Liam Childs'

import argparse


def extract(fname, genes):
    gbk = GenBankFile(fname)
    if len(options.paths) == 0 and len(options.types) == 0:
        sys.stdout.write('>whole_sequence\n')
        if options.wrap:
            for i in xrange(0, len(gbk.seq), options.wrap):
                sys.stdout.write(gbk.seq[i:i + options.wrap])
                sys.stdout.write('\n')

        else:
            sys.stdout.write(gbk.seq)
            sys.stdout.write('\n')

    extract_genes(genes, gbk, options)
    if len(options.paths) > 0:
        extract_paths(gbk, options)
    if len(options.types) > 0:
        extract_type(gbk, options)


def extract_genes(genes, gbk, options):
    for gene in genes:
        ftr = None
        for typ, ftrs in gbk.ftrs.iteritems():
            for f in ftrs:
                if 'label' in f and f['label'] == gene:
                    ftr = f
                    break
            if ftr != None:
                break
        if ftr == None:
            sys.stdout.write('Unable to find {}\n'.format(gene))
            continue

        hdr = [gene]
        if options.ext5 != 0:
            hdr.append('atg:{}'.format(options.ext5))
        if options.ext3 != 0:
            hdr.append('end:{}'.format(options.ext3))
        rng5p = ftr['range'].get5pInterval(-options.ext5)
        rng3p = ftr['range'].get3pInterval(options.ext3)
        rng = rng5p | ftr['range'] | rng3p
        seq = rng.get_sub_seq(gbk.seq)

        sys.stdout.write('>%s{}%s{}'.format(' '.join(hdr), seq))


def extract_paths(gbk, options):
    for typ, qua, val in options.paths:
        cnt = 0
        for ftr in gbk.ftrs[typ]:
            if ftr[qua] == val:
                rng5p = ftr['range'].get5pInterval(-options.ext5)
                rng3p = ftr['range'].get3pInterval(options.ext3)
                rng = rng5p | ftr['range'] | rng3p
                seq = rng.get_sub_seq(gbk.seq)
                hdr = ['{}_{}_{}.{}'.format(typ, qua, val, cnt)]
                if options.ext5 != 0:
                    hdr.append('atg:{}'.format(options.ext5))
                if options.ext3 != 0:
                    hdr.append('end:{}'.format(options.ext3))
                sys.stdout.write('>{}\n{}\n'.format(' '.join(hdr), seq))
                cnt += 1
        if cnt == 0:
            sys.stdout.write('Path {} {} {}does not exist\n'.format(typ, qua, val))


def extract_type(gbk, options):
    for typ in options.types:
        cnt = 0
        for ftr in gbk.ftrs[typ]:
            rng = ftr['range']
            rng.adj5p(-options.ext5)
            rng.adj3p(options.ext3)
            seq = rng.get_sub_seq(gbk.seq)
            hdr = ['{}.{}'.format(typ, cnt)]
            if options.ext5 != 0:
                hdr.append('atg:{}'.format(options.ext5))
            if options.ext3 != 0:
                hdr.append('end:{}'.format(options.ext3))
            sys.stdout.write('>{}\n{}\n'.format(' '.join(hdr), seq))
            cnt += 1
        if cnt == 0:
            sys.stdout.write('Path %s does not exist\n'%(typ))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument

    add_arg('input')
    add_arg('genes', nargs='+')
    add_arg('-5', '--5p', action='store', type=int, dest='ext5', default=0,
            help='Extend the sequence in the  5\'direction.')
    add_arg('-3', '--3p', action='store', type=int, dest='ext3', default=0,
            help='Extend the sequence in the  3\'direction.')
    add_arg('-p', '--path', action='append', nargs=3, dest='paths', default=[],
            help='Extract a sequence using the given paths (eg. CDS gene nptII)')
    add_arg('-t', '--type', action='append', nargs=1, default=[],
            dest='types', help='Extract a feature type (eg. CDS)')
    add_arg('-w', '--wrap', type=int,
            help='Wrap the sequence')

    parser.set_defaults(func=init_extract)
    return parser


def init_extract(args):
    extract(args.input, args.genes)


if __name__ == '__main__':
    import sys
    sys.exit(main())
