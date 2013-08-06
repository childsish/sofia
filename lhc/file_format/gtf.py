from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_interval import interval

def iterGtf(fname):
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', 0)
    column_builder.registerColumn('fr', 3, int)
    column_builder.registerColumn('to', 4, int)
    column_builder.registerColumn('strand', 6)
    column_builder.registerColumn('type', 2)
    column_builder.registerColumn('attr', 8)
    
    field_builder = FieldBuilder()
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('type')
    field_builder.registerField('attr', parseAttributes)
    
    for fields in iterCsv(fname, column_builder, field_builder):
        yield fields

def parseInterval(cols):
    return interval(cols.chr, cols.fr - 1, cols.to, cols.strand)

def parseAttributes(cols):
    parts = [part.strip().split(' ', 1) for part in cols.attr.split(';') if part != '']
    for i in xrange(len(parts)):
        if parts[i][1].startswith('"'):
            parts[i][1] = parts[i][1][1:-1]
        else:
            parts[i][1] = int(parts[i][1])
    return dict(parts)