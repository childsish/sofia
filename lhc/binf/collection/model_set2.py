import sqlite3
import itertools

from operator import attrgetter
from lhc.tools import argsort
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.collection.nested_containment_list import getTables

class ModelSet(object):
    def __init__(self, fname, mdls=[]):
        self.conn = sqlite3.connect(fname)
        self._createTables()
        self._insertModels(mdls)
        self._createIndices()
    
    def get(self, key, fetch_type=Exon.TYPE.gene):
        assert fetch_type in (Exon.TYPE.gene, Exon.TYPE.transcript)
        
        cur = self.conn.cursor()
        qry = '''SELECT model.id, model.chromosome, interval.start, interval.stop, model.strand, model.type, model.name, model.parent
        FROM model AS gene, model, interval
        WHERE gene.name = ? AND
            gene.type = "{}" AND
            model.left >= gene.left AND
            model.right <= gene.right AND
            interval.id = model.interval
        ORDER BY model.id, model.ordering'''.format(fetch_type)
        
        res = {}
        res_id = None
        for id, chm, start, stop, strand, type_, name, parent in cur.execute(qry, (key,)):
            if type_ == fetch_type:
                res_id = id
            ivl = Interval(chm, start, stop, strand)
            if type_ == Exon.TYPE.gene:
                res[id] = Gene(name, ivl)
            elif type_ == Exon.TYPE.transcript:
                res[id] = Transcript(name, ivl)
                res[parent].transcripts[name] = res[id]
            else:
                res[id] = Exon(ivl, type_)
                res[parent].exons.append(res[id])
        return res[res_id]
    
    def intersect(self, ivl, fetch_type=Exon.TYPE.gene):
        qry = '''
            WITH RECURSIVE
                cumulative_intervals(interval, sublist) AS (
                    SELECT i.id, i.sublist
                    FROM interval AS i, sublist AS s
                    WHERE s.id = 1 AND
                        i.id >= s.interval AND
                        i.id < s.interval + s.size AND
                        i.start < ? AND
                        ? < i.stop
                    UNION
                    SELECT i.id, i.sublist
                    FROM interval AS i, sublist AS s, 
                    WHERE s.id = cumulative_intervals.sublist AND
                        i.id >= s.interval AND
                        i.id < s.interval + s.size AND
                        i.start < ? AND
                        ? < i.stop
                )
            SELECT model.name
            FROM model, interval
            WHERE model.interval == cumulative_intervals.interval AND
                model.chromosome == ? AND
                model.type == ?
        '''
        return [self.get(name, fetch_type) for name, in\
            cur.execute(qry, (ivl.stop, ivl.start, ivl.stop, ivl.start, ivl.chromosome, fetch_type))]

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.commit()
            self.conn.close()
    
    def _createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE interval (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start INTEGER,
            stop INTEGER,
            sublist INTEGER REFERENCES sublist(id) DEFERRABLE INITIALLY DEFERRED)''')
        cur.execute('''CREATE TABLE sublist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interval INTEGER REFERENCES interval(id),
            size INTEGER)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interval INTEGER REFERENCES interval(id),
            chromosome TEXT,
            strand TEXT,
            type TEXT,
            name TEXT,
            ordering INTEGER,
            parent INTEGER,
            left INTEGER,
            right INTEGER,
            FOREIGN KEY (parent) REFERENCES model(id)
        )''')
    
    def _insertModels(self, mdls):
        flat_mdls, ivls = self._flattenModels(mdls)
        ivl_table, grp_table, idxs = getTables(ivls)
        ids = [mdl[0] for mdl in flat_mdls]
        for mdl, idx in itertools.izip(flat_mdls, idxs):
            mdl[0] = ids[idx]
        
        self.conn.executemany('INSERT INTO interval VALUES (NULL, ?, ?, ?)', ivl_table)
        self.conn.executemany('INSERT INTO sublist VALUES (NULL, ?, ?)', grp_table)
        self.conn.executemany('INSERT INTO model VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)', flat_mdls)
    
    def _flattenModels(self, mdls):
        def insertTranscripts(gene, gene_id):
            for transcript_ordering, transcript in enumerate(gene.transcripts.itervalues()):
                ivl_id = insertInterval(transcript.ivl)
                flat_mdls.append([ivl_id, transcript.ivl.chr, transcript.ivl.strand, 'transcript', transcript.name, transcript_ordering, gene_id, 0, 0])
                transcript_id = len(flat_mdls)
                updateLeft(flat_mdls[transcript_id - 1])
                insertExons(transcript, transcript_id)
                updateRight(flat_mdls[transcript_id - 1])
        
        def insertExons(transcript, transcript_id):
            for exon_ordering, exon in enumerate(transcript.exons):
                ivl_id = insertInterval(exon.ivl)
                flat_mdls.append([ivl_id, exon.ivl.chr, exon.ivl.strand, exon.type, None, exon_ordering, transcript_id, 0, 0])
                exon_id = len(flat_mdls)
                updateLeft(flat_mdls[exon_id - 1])
                updateRight(flat_mdls[exon_id - 1])
        
        def insertInterval(interval):
            ivls.append(interval)
            return len(ivls)
        
        def updateLeft(flat_mdl):
            flat_mdl[7] = idx_generator.next()
        
        def updateRight(flat_mdl):
            flat_mdl[8] = idx_generator.next()
        
        flat_mdls = []
        ivls = []
        idx_generator = itertools.count()
        
        for gene_ordering, gene in enumerate(mdls):
            ivl_id = insertInterval(gene.ivl)
            flat_mdls.append([ivl_id, gene.ivl.chr, gene.ivl.strand, 'gene', gene.name, gene_ordering, None, 0, 0])
            gene_id = len(flat_mdls)
            updateLeft(flat_mdls[gene_id - 1])
            insertTranscripts(gene, gene_id)
            updateRight(flat_mdls[gene_id - 1])
        return flat_mdls, ivls
    
    def _createIndices(self):
        cur = self.conn.cursor()
        cur.execute('CREATE INDEX IF NOT EXISTS model_name_idx ON model(name)')
        cur.execute('CREATE INDEX IF NOT EXISTS model_position_idx ON model(interval, chromosome, type)')
        cur.execute('CREATE INDEX IF NOT EXISTS model_extent_idx ON model(left, right)')
        cur.execute('CREATE INDEX IF NOT EXISTS interval_idx ON interval(id, start, stop)')