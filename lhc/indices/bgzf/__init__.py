__author__ = 'Liam Childs'

import gzip
import json
import os

from .point_index import PointIndex
from .interval_index import IntervalIndex


def load_index(filename):
    if not os.path.exists('{}.lci'.format(filename)):
        raise OSError('{} missing index'.format(os.path.basename(filename)))

    index_file = gzip.open('{}.lci'.format(filename))
    state = json.load(index_file)
    state['index_classes'] = [{'P': PointIndex, 'I': IntervalIndex}[index_class] for index_class in state['index_classes']]
    index = {'P': PointIndex, 'I': IntervalIndex}[state['type']]()
    index.__setstate__(state)
    return index
