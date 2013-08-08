from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_interval import interval

def iterMaf(fname):
    column_builder = ColumnBuilder()
    column_builder.registerColumn('chr', 4)
    column_builder.registerColumn('fr', 5, int)
    column_builder.registerColumn('to', 6, int)
    column_builder.registerColumn('strand', 7)
    column_builder.registerColumn('type', 9)
    column_builder.registerColumn('ref', 10)
    column_builder.registerColumn('allele1', 11)
    column_builder.registerColumn('allele2', 12)
    column_builder.registerColumn('genotype_id', 15)
    
    field_builder = FieldBuilder()
    field_builder.registerField('ivl', parseInterval)
    field_builder.registerField('type')
    field_builder.registerField('ref')
    field_builder.registerField('allele1')
    field_builder.registerField('allele2')
    field_builder.registerField('genotype_id')
    
    for fields in iterCsv(fname, column_builder, field_builder, skip=1):
        yield fields

def parseInterval(cols):
    return interval(cols.chr, cols.fr - 1, cols.to, cols.strand)

