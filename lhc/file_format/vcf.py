import os

from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.tools import enum
from lhc.binf.genomic_coordinate import Interval

VARIANT_TYPE = enum(['VARIANT', 'SNP'])

class VcfParser(object):

    CHR = 0
    POS = 1
    ID = 2
    REF = 3
    ALT1 = 4
    ALT2 = 4
    QUAL = 5
    ATTR = 7

    def __init__(self, type=VARIANT_TYPE.SNP):
        self.type = type

        self.column_builder = ColumnBuilder()
        self.column_builder.registerColumn('chr', VcfParser.CHR)
        self.column_builder.registerColumn('pos', VcfParser.POS, int)
        self.column_builder.registerColumn('id', VcfParser.ID)
        self.column_builder.registerColumn('ref', VcfParser.REF)
        self.column_builder.registerColumn('alt', VcfParser.ALT1)
        self.column_builder.registerColumn('qual', VcfParser.QUAL)
        self.column_builder.registerColumn('attr', VcfParser.ATTR)
        
        #TODO: Find a better place
        self.field_builder = FieldBuilder()
        if type == VARIANT_TYPE.SNP:
            self.field_builder.registerField('id')
            self.field_builder.registerField('pos', self._parsePosition)
            self.field_builder.registerField('ref')
            self.field_builder.registerField('alt1', lambda cols:cols.alt)
            self.field_builder.registerField('alt2', lambda cols:cols.alt)
            self.field_builder.registerField('qual', self._parseQuality)
            self.field_builder.registerField('attr', self._parseAttributes)
            self.field_builder.registerField('genotype_id',
                lambda cols:os.basename(fname).rsplit('.')[0])
        elif type == VARIANT_TYPE.VARIANT:
            self.field_builder.registerField('id')
            self.field_builder.registerField('ivl', self._parseInterval)
            self.field_builder.registerField('type', lambda cols:'SNP')
            self.field_builder.registerField('ref')
            self.field_builder.registerField('alt1', lambda cols:cols.alt)
            self.field_builder.registerField('alt2', lambda cols:cols.alt)
            self.field_builder.registerField('qual', self._parseQuality)
            self.field_builder.registerField('attr', self._parseAttributes)
            self.field_builder.registerField('genotype_id',
                lambda cols:os.basename(fname).rsplit('.')[0])
        else:
            raise ValueError('Unrecognised variant type: %s'%type)
        
    def iterVariants(self, fname, skip=0):
        return iterCsv(fname, self.column_builder, self.field_builder, skip)
    
    def _parsePosition(self, cols):
        return Position(cols.chr, cols.pos - 1, cols)

    def _parseInterval(self, cols):
        return Interval(cols.chr, cols.pos - 1, cols.pos)

    def _parseQuality(self, cols):
        if cols.qual == '.':
            return None
        return float(cols.qual)

    def _parseAttributes(self, cols):
        return dict(part.strip().split('=', 1)\
            for part in cols.attr.strip().split(';'))

