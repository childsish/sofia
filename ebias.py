import argparse

from ebias.subcommands import aggregate, index

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    aggregate_parser = subparsers.add_parser('aggregate')
    aggregate.defineParser(aggregate_parser)
    
    #index_parser = subparsers.add_parser('index')
    #index_parser.defineParser(index_parser)
    
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
