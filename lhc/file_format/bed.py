from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_coordinate import Interval

def iterBed(fname):
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', 0)
    column_builder.registerColumn('fr', 1, int)
    column_builder.registerColumn('to', 2, int)
    column_builder.registerColumn('name', 3)
    column_builder.registerColumn('score', 4)
    column_builder.registerColumn('strand', 5)
    
    field_builder = FieldBuilder()
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('name')
    field_builder.registerField('score')
    field_builder.registerField('strand')
    
    for fields in iterCsv(fname, column_builder, field_builder, skip=1):
        yield fields

def parseInterval(cols):
    return Interval(cols.chr, cols.fr, cols.to)

