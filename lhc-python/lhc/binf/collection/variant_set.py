import sqlite3

from lhc.binf.variant import Variant
from lhc.binf.genomic_coordinate import Interval
from lhc.collection.sqlite.interval_module import IntervalModule

class VariantSet(object):
    
    ALTSEP = '/'
    
    def __init__(self, fname, vnts=None):
        """Create a variant set
        
        :param str fname: the file where the variants are kept/to be kept
        :param iter vnts: an iterable container of the variants
        """
        self.conn = sqlite3.connect(fname)
        self.interval_module = IntervalModule(self.conn)
        if vnts is not None:
            self._createTables()
            self._insertVariants(vnts)
            self._createIndices()
    
    def overlap(self, ivl):
        def createVariant(chr, start, stop, alt, type, quality, genotype):
            alt = map(str, alt.split(VariantSet.ALTSEP))
            type = map(str, type.split(VariantSet.ALTSEP))
            ivl = Interval(chr, start, stop)
            return Variant(ivl, alt, type, quality, genotype)
        
        cur = self.conn.cursor()
        
        qry = '''WITH overlap(id, start, stop) AS ({interval_query})
            SELECT v.chr, o.start, o.stop, v.alt, v.type, v.quality, v.genotype
            FROM variant AS v, overlap AS o
            WHERE v.interval = o.id
        '''.format(interval_query=self.interval_module.getQuery(ivl))
        rows = cur.execute(qry, {'start': ivl.start, 'stop': ivl.stop})
        return [createVariant(chr, start, stop, alt, type, quality, genotype)\
            for chr, start, stop, alt, type, quality, genotype in rows\
            if chr == ivl.chr]
    
    def _createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE genotype (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )''')
        self.interval_module.createTable()
        cur.execute('''CREATE TABLE variant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chr TEXT,
            interval REFERENCES interval(id),
            alt TEXT,
            type TEXT,
            quality REAL,
            genotype REFERENCES genotype(id)
        )''')
    
    def _insertVariants(self, vnts):
        cur = self.conn.cursor()
        genotypes = {None: None}
        qry = 'INSERT INTO variant VALUES (NULL, :chr, :interval, :alt, :type, :quality, :genotype)'
        for vnt in vnts:
            if vnt.genotype not in genotypes:
                cur.execute('INSERT INTO genotype VALUES (NULL, :name)',
                    {'name': vnt.genotype})
                genotypes[vnt.genotype] = cur.lastrowid
            genotype = genotypes[vnt.genotype]
            interval = self.interval_module.insertInterval(vnt.ivl)
            cur.execute(qry,
                {'chr': vnt.ivl.chr,
                 'interval': interval,
                 'alt': VariantSet.ALTSEP.join(vnt.alt),
                 'type': VariantSet.ALTSEP.join(vnt.type),
                 'quality': vnt.quality,
                 'genotype': genotype})
    
    def _createIndices(self):
        self.interval_module.createIndex()
