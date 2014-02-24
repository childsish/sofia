import os

from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.tools import enum
from lhc.binf.genomic_coordinate import Interval

VARIANT_TYPE = enum(['VARIANT', 'SNP'])

class CnsParser(object):

    CHR = 0
    POS = 1
    REF = 2
    ALT1 = 3
    ALT2 = 3
    QUAL = 4

    def __init__(self, type=VARIANT_TYPE.SNP):
        self.type = type

        column_builder = ColumnBuilder()
        column_builder.registerColumn('chr', CnsParser.CHR)
        column_builder.registerColumn('pos', CnsParser.POS, int)
        column_builder.registerColumn('ref', CnsParser.REF)
        column_builder.registerColumn('alt', CnsParser.ALT1)
        column_builder.registerColumn('qual', CnsParser.QUAL)
        
        if type == VARIANT_TYPE.SNP:
            field_builder = FieldBuilder()
            field_builder.registerField('pos', self._parsePosition)
            field_builder.registerField('ref')
            field_builder.registerField('alt1', lambda cols:cols.alt)
            field_builder.registerField('alt2', lambda cols:cols.alt)
            field_builder.registerField('qual', self._parseQuality)
            field_builder.registerField('genotype_id',
                lambda cols:os.path.basename(fname).rsplit('.')[0])
        elif type == VARIANT_TYPE.VARIANT:
            field_builder = FieldBuilder()
            field_builder.registerField('ivl', self._parseInterval)
            field_builder.registerField('type', lambda cols:'SNP')
            field_builder.registerField('ref')
            field_builder.registerField('alt1', lambda cols:cols.alt)
            field_builder.registerField('alt2', lambda cols:cols.alt)
            field_builder.registerField('qual', self._parseQuality)
            field_builder.registerField('genotype_id',
                lambda cols:os.path.basename(fname).rsplit('.')[0])
        
    def iterVariants(self, fname):
        """Iterate through a CNS file (Some sort of variant format).
        """
        return iterCsv(fname, column_builder, field_builder, skip=1)

    def _parsePosition(self, cols):
        return Position(cols.chr, cols.pos - 1, cols)

    def _parseInterval(self, cols):
        return Interval(cols.chr, cols.pos - 1, cols.pos)

    def _parseQuality(self, cols):
        if cols.qual == '.':
            return None
        return float(cols.qual)
