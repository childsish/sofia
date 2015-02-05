from lhc.interval import Interval, IntervalBinner

binner = IntervalBinner()
types = {
    's': str,
    'f': float,
    'i': int,
    'v': lambda start, stop: binner.get_bin(Interval(start, stop))
}


def convert_args_to_types(args):
    return [([int(idx) for idx in arg[:-1].split(',')], types[arg[-1]]) for arg in args]


def extract_typed_columns(line, column_types=(([1], str),), sep='\t'):
    parts = line.rstrip('\r\n').split(sep)
    return (t(*[parts[idx] for idx in idxs]) for idxs, t in column_types)
