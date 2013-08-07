'''
Created on 05/08/2013

@author: Liam Childs
'''

import sqlite3

from collections import defaultdict
from lhc.binf.genomic_interval import interval

class Model(object):
    
    def __init__(self, name, ivl, type):
        self.name = name
        self.ivl = ivl
        self.type = type
        self.children = []

class ModelSet(object):
    
    def __init__(self, fname, mode='w'):
        self.conn = sqlite3.connect(fname)
        self.createTables()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.commit()
            self.conn.close()
    
    def __getitem__(self, key):
        ''' Warning. Requires in order insertion of segments. '''
        if isinstance(key, basestring):
            return self.getModelById(key)
        elif isinstance(key, interval):
            return self.getModelsInInterval(key)
        raise TypeError('Unknown type used to get gene models: %s'%type(key))
    
    def createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE VIRTUAL TABLE interval
            USING rtree(id, ivl_fr, ivl_to);''')
        cur.execute('''CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chr TEXT,
            interval_id REFERENCES interval(id),
            type TEXT,
            strand TEXT,
            parent_id,
            FOREIGN KEY(parent_id) REFERENCES model(id)
        );''')
        cur.execute('''CREATE TABLE IF NOT EXISTS identifier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id REFERENCES model(id),
            value TEXT,
            type TEXT
        );''')
    
    def addModelSegment(self, ivl, type, parent_id=None):
        ''' Warning. Requires in order insertion of segments. '''
        cur = self.conn.cursor()
        qry = 'INSERT INTO interval VALUES (NULL, ?, ?)'
        cur.execute(qry, (ivl.start, ivl.stop))
        interval_id = cur.lastrowid
        qry = 'INSERT INTO model VALUES (NULL, ?, ? ,?, ?, ?)'
        cur.execute(qry, (ivl.chr, interval_id, type, ivl.strand, parent_id))
        model_id = cur.lastrowid
        return model_id
    
    def addIdentifier(self, model_id, value, type='PRIMARY'):
        cur = self.conn.cursor()
        qry = 'SELECT id FROM identifier WHERE model_id = :model_id AND type = :type'
        id = cur.execute(qry, locals()).fetchone()
        qry = 'INSERT INTO identifier VALUES (NULL, :model_id, :value, :type)' if id is None else\
            'UPDATE identifier SET value = :value WHERE model_id = :model_id AND type = :type'
        cur.execute(qry, locals())
        return cur.lastrowid

    def finaliseIntervals(self):
        pass
    
    def getModelById(self, key):
        cur = self.conn.cursor()
        
        qry = '''SELECT model.id, model.chr, model.type, model.strand,
                interval.ivl_fr, interval.ivl_to
            FROM identifier, model, interval
            WHERE
                interval.id = model.interval_id AND
                model.id = identifier.model_id AND
                identifier.value = ?;
        '''
        res_id, chm, typ, strand, fr, to = cur.execute(qry, (key,)).fetchone()
        models = {}
        children = defaultdict(list)
        qry = '''SELECT identifier.value, model.id, model.type, model.strand,
                model.parent_id, interval.ivl_fr, interval.ivl_to
            FROM identifier, model, interval
            WHERE
                identifier.type = 'PRIMARY' AND
                identifier.model_id = model.id AND
                model.chr = ? AND
                model.interval_id = interval.id AND
                interval.ivl_fr >= ? AND
                interval.ivl_to <= ?;'''
        rows = cur.execute(qry, (chm, fr, to))
        for name, id, typ, strand, parent, fr, to in rows:
            models[id] = Model(name, interval(chm, fr, to, strand), typ)
            if parent is not None:
                children[parent].append(id)
        for parent_id, child_ids in children.iteritems():
            models[parent_id].children =\
                [models[child_id] for child_id in child_ids]
        return models[res_id]
    
    def getModelsInInterval(self, ivl):
        return []

