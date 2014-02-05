from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_interval import interval

def iterVcf(fname):
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', 0)
    column_builder.registerColumn('pos', 1, int)
    column_builder.registerColumn('id', 2)
    column_builder.registerColumn('ref', 3)
    column_builder.registerColumn('alt', 4)
    column_builder.registerColumn('qual', 5)
    column_builder.registerColumn('attr', 7)
    
    field_builder = FieldBuilder()
    field_builder.registerField('id')
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('ref')
    field_builder.registerField('alt')
    field_builder.registerField('qual', parseQuality)
    field_builder.registerField('attr', parseAttributes)
    
    for fields in iterCsv(fname, column_builder, field_builder, skip=1):
        yield fields

def parseInterval(cols):
    return interval(cols.chr, cols.pos, cols.pos)

def parseQuality(cols):
    if cols.qual == '.':
        return None
    return float(cols.qual)

def parseAttributes(cols):
    return dict(part.strip().split('=', 1)\
        for part in cols.attr.strip().split(';'))

