import os

from lhc.dynamic_pyyaml import load
from lhc.binf.interval import Interval as interval
from collections import namedtuple
from functools import partial

def iterTable(fname, typ=None, cfg=None):
    def initCfgObj(typ, cfg):
        if cfg is None:
            mname = os.path.join(os.path.dirname(os.path.abspath(__file__)
            infile = open(mname, '../data/table_columns.yaml'))
            cfgs = load(infile)
            infile.close()
            typ = fname.rsplit('.', 1)[1] if typ is None else typ
            cfg = cfgs[typ] if cfg in cfgs else {}
        return cfg
    
    def initColumnDefs(cfg, fname)
        infile = open(fname)
        line = infile.readline()
        infile.close()
        if 'columns' not in cfg:
            cfg['columns'] = [{'name': part.strip()}\
                for part in line.strip().split('\t')]
        for i, col in enumerate(cfg['columns']):
            col['type'] = __builtins__[col['type']] if 'type' in col else str
            if 'idx' not in col:
                col['idx'] = i
    
    def initFieldDefs(cfg):
        if 'fields' not in cfg:
            cfg['fields'] = [{'name': col.name} for col in cfg.columns]
        for field in cfg.fields:
            if 'init' not in field:
                field['init'] = field.name
    
    cfg = initCfgObj(typ, cfg)
    initColumnDefs(cfg, fname)
    initFieldDefs(cfg)
    Entry = namedtuple('Entry', [field.name for field in cfg.fields])
    infile = open(fname)
    line = infile.next()
    while line.startswith('#'):
        line = infile.next()
    if 'header' in cfg and cfg.header:
        line = infile.next()
    while line != '':
        parts = line.strip().split('\t')
        cols = {col.name: col.type(parts[col.idx]) for col in cfg.columns}
        yield Entry(**{field.name: eval(field.init, cols)\
            for field in cfg['fields']})
        line = infile.next()
    infile.close()
