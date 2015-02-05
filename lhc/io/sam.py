import argparse

from sam_ import clip, filter


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    clip_parser = subparsers.add_parser('clip')
    clip.define_parser(clip_parser)
    
    filter_parser = subparsers.add_parser('filter')
    filter.define_parser(filter_parser)

    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
