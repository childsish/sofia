#!/usr/bin/env python3
import argparse
import sys
import time
import random

from collections import Counter
from lhc.random.reservoir import reservoir


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('-s', '--seed',
                        help='random seed')
    parser.add_argument('-i', '--iterations', type=int, default=10000,
                        help='number of iterations to run')
    parser.set_defaults(func=reservoir_init)
    return parser


def reservoir_init(args):
    random.seed(args.seed if args.seed else time.time())

    combinations = [
        (10, 1),
        (10, 2),
        (10, 5),
        (100, 1),
        (100, 10),
        (100, 20),
        (100, 50),
        (1000, 1),
        (1000, 10),
        (1000, 100),
        (1000, 200),
        (1000, 500),
        (10000, 1),
        (10000, 10),
        (10000, 100),
        (10000, 1000),
        (10000, 2000),
        (10000, 5000),
    ]
    sys.stdout.write('n\tk\titem\tcount\n')
    for n, k in combinations:
        counter = Counter()
        for i in range(args.iterations):
            counter.update(reservoir(iter(range(n)), k))
        for item, count in sorted(counter.items()):
            sys.stdout.write('{}\t{}\t{}\t{}\n'.format(n, k, item, count))

if __name__ == '__main__':
    sys.exit(main())
