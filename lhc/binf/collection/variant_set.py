import sqlite3
from lhc.binf.genomic_coordinate import Interval

class VariantSet(object):
    
    MINBIN = 3
    MAXBIN = 7
    
    def __init__(self, fname, vnts=None):
        self.conn = sqlite3.connect(fname)
        if vnts is not None:
            self._createTables()
            self._insertVariants(vnts)
            self._createIndices()
    
    def overlap(self, ivl):
        cur = self.conn.cursor()
        getOverlappingBins = self._getOverlappingBins
        
        qry1 = '''SELECT genotype, chr, start, stop, alt, quality, allele, type, bin
            FROM variant
            WHERE bin == {bin} AND
                chr == "{chr}"'''
        qry2 = '''SELECT genotype, chr, start, stop, alt, quality, allele, type, bin
            FROM variant
            WHERE bin BETWEEN {lower} AND {upper} AND
                chr == "{chr}"'''
        
        qry = []
        bins = getOverlappingBins(ivl.start, ivl.stop)
        for bin in bins:
            if bin[0] == bin[1]:
                qry.append(qry1.format(chr=ivl.chr, bin=bin[0]))
            else:
                qry.append(qry2.format(chr=ivl.chr, lower=bin[0], upper=bin[1]))
        rows = cur.execute(' UNION '.join(qry))
        return [Interval(chr, start, stop) for genotype, chr, start, stop, alt, quality, allele, type, bin in rows if start <= ivl.stop and ivl.start < stop]
    
    def _createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE genotype (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )''')
        cur.execute('''CREATE TABLE variant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genotype REFERENCES genotype(id),
            chr TEXT,
            start INTEGER,
            stop INTEGER,
            alt TEXT,
            quality REAL,
            allele INTEGER,
            type TEXT,
            bin INTEGER
        )''')
    
    def _insertVariants(self, vnts):
        cur = self.conn.cursor()
        getBin = self._getBin
        genotypes = {}
        for vnt in vnts:
            if vnt.genotype not in genotypes:
                cur.execute('INSERT INTO genotype VALUES (NULL, :name)',
                    {'genotype': vnt.genotype})
                genotypes[vnt.genotype] = cur.lastrowid
            genotype = genotypes[vnt.genotype]
            cur.execute('''INSERT INTO variant VALUES (NULL, :genotype, :chr,
                    :start, :stop, :bin)''',
                {'genotype': genotype, 'chr': vnt.chr, 'start': vnt.start,
                    'stop': vnt.stop, 'bin': getBin(vnt.start, vnt.stop)})
    
    def _createIndices(self):
        cur = self.conn.cursor()
        cur.execute('CREATE INDEX IF NOT EXISTS variant_idx ON variant(bin, chr)')
        
    def _getBin(self, ivl):
        for i in range(VariantSet.MINBIN, VariantSet.MAXBIN + 1):
            binLevel = 10 ** i
            if int(ivl.start / binLevel) == int(ivl.end / binLevel):
                return int(i * 10 ** (VariantSet.MAXBIN + 1) + int(ivl.start / binLevel))
        return int((VariantSet.MAXBIN + 1) * 10 ** (VariantSet.MAXBIN + 1))
    
    def _getOverlappingBins(self, ivl):
        res = []
        bigBin = int((VariantSet.MAXBIN + 1) * 10 ** (VariantSet.MAXBIN + 1))
        for i in range(VariantSet.MINBIN, VariantSet.MAXBIN + 1):
            binLevel = 10 ** i
            res.append((int(i * 10 ** (VariantSet.MAXBIN + 1) + int(ivl.start / binLevel)),
                        int(i * 10 ** (VariantSet.MAXBIN + 1) + int(ivl.end / binLevel))))
        res.append((bigBin, bigBin))
        return res
