from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_coordinate import Interval

def iterCns(fname):
    """Iterate through a CNS file (Some sort of variant format).
    """
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', 0)
    column_builder.registerColumn('pos', 1, int)
    column_builder.registerColumn('ref', 2)
    column_builder.registerColumn('alt', 3)
    column_builder.registerColumn('qual', 4)
    
    field_builder = FieldBuilder()
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('ref')
    field_builder.registerField('alt')
    field_builder.registerField('qual', parseQuality)
    field_builder.registerField('genotype_id', lambda cols:fname.rsplit('.')[0])
    
    for fields in iterCsv(fname, column_builder, field_builder, skip=1):
        yield fields

def parseInterval(cols):
    return Interval(cols.chr, cols.pos, cols.pos)

def parseQuality(cols):
    if cols.qual == '.':
        return None
    return float(cols.qual)
