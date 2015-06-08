__author__ = 'Liam Childs'

import argparse

from lhc.io.vcf_.iterator import VcfLineIterator, VcfLine


def init(args):
    input = sys.stdin if args.input is None else open(args.input)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    trim_alt(input, output)
    input.close()
    output.close()


def trim_alt(input, output):
    it = VcfLineIterator(input)
    for k, vs in it.hdrs.iteritems():
        for v in vs:
            output.write('{}={}\n'.format(k, v))
    for variant in it:
        poss, refs, alts = _trim_alt(variant.pos, variant.ref, variant.alt)
        tmp = list(variant)
        for pos, ref, alt in zip(poss, refs, alts):
            tmp[1] = pos
            tmp[3] = ref
            tmp[4] = alt
            output.write(str(VcfLine(*tmp)))
            output.write('\n')
    input.close()
    output.close()


def _trim_alt(pos, ref, alt):
    poss = []
    refs = []
    alts = []
    for alt in alt.split(','):
        j = 0
        while j < len(ref) and j < len(alt) and ref[-j - 1] == alt[-j - 1]:
            j += 1
        i = 0
        while i < len(ref) - j - 1 and i < len(alt) - j - 1 and ref[i] == alt[i]:
            i += 1
        poss.append(pos + i)
        refs.append(ref[i:len(ref) - j])
        alts.append(alt[i:len(alt) - j])
    return poss, refs, alts


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument

    add_arg('input', default=None, nargs='?',
            help='The input file (default: stdin).')
    add_arg('output', default=None, nargs='?',
            help='The output file (default: stdout')

    parser.set_defaults(func=init)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
