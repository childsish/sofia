import os
import sqlite3
import itertools

from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon

class ModelSet(object):

    MINBIN = 2
    MAXBIN = 7

    def __init__(self, fname, mdls=None):
        if mdls is None:
            self.conn = sqlite3.connect(fname)
        if mdls is not None:
            if os.path.exists(fname):
                os.remove(fname)
            self.conn = sqlite3.connect(fname)
            self._createTables()
            self._insertModels(mdls)
            self._createIndices()
    
    def get(self, name, fetch_type=Exon.TYPE.gene):
        assert fetch_type in (Exon.TYPE.gene, Exon.TYPE.transcript)
        
        cur = self.conn.cursor()
        qry = '''SELECT m.id, m.chr, m.start, m.stop, m.strand, m.type, m.name, m.parent
        FROM model AS gene, model AS m
        WHERE gene.name = :name AND
            gene.type = :type AND
            m.left >= gene.left AND
            m.right <= gene.right
        ORDER BY m.id, m.ordering'''.format(fetch_type)
        
        res = {}
        res_id = None
        for id, chr, start, stop, strand, type, name, parent in\
                cur.execute(qry, {'name': name, 'type': fetch_type}):
            if type == fetch_type:
                res_id = id
            ivl = Interval(chr, start, stop, strand)
            if type == Exon.TYPE.gene:
                res[id] = Gene(name, ivl)
            elif type == Exon.TYPE.transcript:
                res[id] = Transcript(name, ivl)
                res[parent].transcripts[name] = res[id]
            else:
                res[id] = Exon(ivl, type)
                res[parent].exons.append(res[id])
        return res[res_id]
    
    def intersect(self, ivl, fetch_type=Exon.TYPE.gene):
        cur = self.conn.cursor()
        getOverlappingBins = self._getOverlappingBins
        
        qry1 = '''SELECT name
            FROM model
            WHERE bin = {bin} AND
                type = :type AND
                chr = "{chr}"'''
        qry2 = '''SELECT name
            FROM model
            WHERE bin BETWEEN {lower} AND {upper} AND
                type = :type AND
                chr = "{chr}"'''
        
        qry = []
        bins = getOverlappingBins(ivl)
        for bin in bins:
            if bin[0] == bin[1]:
                qry.append(qry1.format(chr=ivl.chr, bin=bin[0]))
            else:
                qry.append(qry2.format(chr=ivl.chr, lower=bin[0], upper=bin[1]))
        rows = cur.execute(' UNION '.join(qry), {'type': fetch_type})
        
        return [self.get(name, fetch_type) for name, in rows]

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.commit()
            self.conn.close()
    
    def _createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chr TEXT,
            start INTEGER,
            stop INTEGER,
            strand TEXT,
            type TEXT,
            name TEXT,
            ordering INTEGER,
            parent INTEGER,
            left INTEGER,
            right INTEGER,
            bin INTEGER,
            FOREIGN KEY (parent) REFERENCES model(id)
        )''')
    
    def _insertModels(self, mdls):
        cur = self.conn.cursor()
        insert_qry = '''INSERT INTO model VALUES (NULL, :chr, :start, :stop,
            :strand, :type, :name, :ordering, :parent, :left, :right, :bin)'''
        update_qry = 'UPDATE model SET right = :right WHERE id = :id'
        counter = itertools.count()
        for gene_idx, gene in enumerate(mdls):
            cur.execute(insert_qry, {
                'chr': gene.ivl.chr,
                'start': gene.ivl.start,
                'stop': gene.ivl.stop,
                'strand': gene.ivl.strand,
                'type': 'gene',
                'name': gene.name,
                'ordering': gene_idx,
                'parent': None,
                'left': counter.next(),
                'right': None,
                'bin': self._getBin(gene.ivl)})
            gene_id = cur.lastrowid
            for transcript_idx, transcript_key in enumerate(gene.transcripts):
                transcript = gene.transcripts[transcript_key]
                cur.execute(insert_qry, {
                    'chr': transcript.ivl.chr,
                    'start': transcript.ivl.start,
                    'stop': transcript.ivl.stop,
                    'strand': transcript.ivl.strand,
                    'type': 'transcript',
                    'name': transcript.name,
                    'ordering': transcript_idx,
                    'parent': gene_id,
                    'left': counter.next(),
                    'right': None,
                    'bin': self._getBin(transcript.ivl)})
                transcript_id = cur.lastrowid
                for exon_idx, exon in enumerate(transcript.exons):
                    cur.execute(insert_qry, {
                        'chr': exon.ivl.chr,
                        'start': exon.ivl.start,
                        'stop': exon.ivl.stop,
                        'strand': exon.ivl.strand,
                        'type': exon.type,
                        'name': None,
                        'ordering': exon_idx,
                        'parent': transcript_id,
                        'left': counter.next(),
                        'right': counter.next(),
                        'bin': self._getBin(exon.ivl)})
                cur.execute(update_qry, {'right': counter.next(), 'id': transcript_id})
            cur.execute(update_qry, {'right': counter.next(), 'id': gene_id})
    
    def _createIndices(self):
        cur = self.conn.cursor()
        cur.execute('CREATE INDEX IF NOT EXISTS model_name_idx ON model(name, type, left, right)')
        cur.execute('CREATE INDEX IF NOT EXISTS variant_idx ON model(bin, type, chr)')
    
    def _getBin(self, ivl):
        for i in range(ModelSet.MINBIN, ModelSet.MAXBIN + 1):
            binLevel = 10 ** i
            if int(ivl.start / binLevel) == int(ivl.stop / binLevel):
                return int(i * 10 ** (ModelSet.MAXBIN + 1) + int(ivl.start / binLevel))
        return int((ModelSet.MAXBIN + 1) * 10 ** (ModelSet.MAXBIN + 1))
    
    def _getOverlappingBins(self, ivl):
        res = []
        bigBin = int((ModelSet.MAXBIN + 1) * 10 ** (ModelSet.MAXBIN + 1))
        for i in range(ModelSet.MINBIN, ModelSet.MAXBIN + 1):
            binLevel = 10 ** i
            res.append((int(i * 10 ** (ModelSet.MAXBIN + 1) + int(ivl.start / binLevel)), int(i * 10 ** (ModelSet.MAXBIN + 1) + int(ivl.stop / binLevel))))
        res.append((bigBin, bigBin))
        return res
    
