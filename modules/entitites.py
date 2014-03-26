from collections import namedtuple

Sequence = namedtuple('Sequence',
    ('chr', 'seq'))

Variant = namedtuple('Variant',
    ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'attr', 'samples'))
