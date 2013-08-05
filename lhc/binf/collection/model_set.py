'''
Created on 05/08/2013

@author: Liam Childs
'''

import sqlite3

class ModelSet(object):
    def __init__(self, fname):
        self.conn = sqlite3.connect(fname)
        self.createTables()
    
    def createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS interval USING rtree(id, ivl_fr, ivl_to);''')
        cur.execute('''CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chr TEXT,
            interval_id REFERENCES interval(id),
            type TEXT,
            strand TEXT,
            parent_id,
            FOREIGN KEY(parent_id) REFERENCES model(id)
        );''')
        cur.execute('''CREATE TABLE IF NOT EXISTS closure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id REFERENCES model(id),
            child_id REFERENCES model(id)
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS identifier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id REFERENCES model(id),
            value TEXT,
            type TEXT
        );''')
    
    def addModelSegment(self, chr, ivl, type, strand, parent=None):
        cur = self.conn.cursor()
        parent_id = None if parent is None else self.getIdentifier(parent)
        qry = '''INSERT INTO interval VALUES (NULL, ?, ?)'''
        interval_id = cur.execute(qry, ivl.fr, ivl.to)
        qry = '''INSERT INTO model VALUES (NULL, ?, ? ,?, ?, ?)'''
        model_id = cur.execute(qry, chr, interval_id, type, strand, parent_id)
        parent_id = model_id if parent is None else parent_id
        qry = '''INSERT INTO closure VALUES (NULL, ?, ?)'''
        cur.execute(qry, parent_id, model_id)
        return model_id
    
    def addIdentifier(self, model_id, value, type):
        qry = '''INSERT INTO identifier VALUES (NULL, ?, ?, ?)'''
        cur.execute(qry, model_id, value, type)
    
    def getIdentifier(self, name):
        cur = self.conn.cursor()
        qry = '''SELECT model_id FROM identifier WHERE value = ?'''
        return cur.execute(qry, name)
    
    def getModel(self, name):
        cur = self.conn.cursor()
        qry = '''SELECT model.chr, interval.fr, interval.to, model.type, model.strand
            FROM interval, model, closure, identifier
            WHERE
                interval.id = model.interval_id AND
                model.id = closure.child_id AND
                closure.parent_id = identifier.model_id AND
                identifier.value = ?;
        '''
        gene = None
        transcripts = []
        segments = {}
        rows = cur.execute(qry, name)
        for row in rows:
            if row.type == 'gene':
                gene = Model(row)
            elif row.type == 'transcript':
                transcripts.append(Model(row))
            elif row.type in ('exon',):
                segments[row.parent] = Model(row)
        return gene