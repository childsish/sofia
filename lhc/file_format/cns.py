import os

from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_coordinate import Interval

CHR = 0
POS = 1
REF = 2
ALT1 = 3
ALT2 = 3
QUAL = 4

def iterCns(fname):
    """Iterate through a CNS file (Some sort of variant format).
    """
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', CHR)
    column_builder.registerColumn('pos', POS, int)
    column_builder.registerColumn('ref', REF)
    column_builder.registerColumn('alt', ALT1)
    column_builder.registerColumn('qual', QUAL)
    
    field_builder = FieldBuilder()
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('ref')
    field_builder.registerField('alt')
    field_builder.registerField('qual', parseQuality)
    field_builder.registerField('genotype_id', lambda cols:os.path.basename(fname).rsplit('.')[0])
    
    for fields in iterCsv(fname, column_builder, field_builder, skip=1):
        yield fields

def parseInterval(cols):
    return Interval(cols.chr, cols.pos - 1, cols.pos)

def parseQuality(cols):
    if cols.qual == '.':
        return None
    return float(cols.qual)
