import os

from lhc.dynamic_pyyaml import load
from collections import namedtuple

def iterTable(fname, typ=None):
    typ = fname.rsplit('.')[1] if typ is None else typ
    infile = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        '../data/table_columns.yaml'))
    cfg = load(infile)[typ]
    infile.close()
    cfg['import'] = cfg['import'] if 'import' in cfg else []
    for imp in cfg['import']:
        __import__(imp)
    for i, col in enumerate(cfg.columns):
        col['type'] = __builtins__[col.type] if 'type' in col else str
        if 'idx' not in col:
            col['idx'] = i
    if 'fields' not in cfg:
        cfg['fields'] = [{'name': col.name} for col in cfg.columns]
    for field in cfg.fields:
        if 'init' not in field:
            field['init'] = field.name
    Entry = namedtuple('Entry', [col.name for col in cfg.columns])
    infile = open(fname)
    line = infile.next()
    while line.startswith('#'):
        line = infile.next()
    while line != '':
        parts = line.strip().split('\t')
        cols = {col.name: col.type(parts[col.idx]) for col in cfg.columns}
        yield Entry(**{field.name: eval(field.init, cols)\
            for field in cfg['fields']})
        line = infile.next()
    infile.close()
