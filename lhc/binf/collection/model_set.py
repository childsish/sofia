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
    
    def __init__(self, fname):
        self.conn = sqlite3.connect(fname)
        self.createTables()
    
    def __getitem__(self, key):
        ''' Warning. Requires in order insertion of segments. '''
        if isinstance(key, basestring):
            return self.getModelById(key)
        elif isinstance(key, interval):
            return self.getModelsInInterval(key)
        raise TypeError('Unknown type used to get gene models: %s'%type(key))
    
    def createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS interval USING rtree(id, ivl_fr, ivl_to);''')
        cur.execute('''CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chr TEXT,
            interval_id REFERENCES interval(id),
            type TEXT,
            strand TEXT
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
    
    def addModelSegment(self, ivl, type, parent_id=None):
        ''' Warning. Requires in order insertion of segments. '''
        cur = self.conn.cursor()
        qry = 'INSERT INTO interval VALUES (NULL, ?, ?)'
        cur.execute(qry, (ivl.fr, ivl.to))
        interval_id = cur.lastrowid
        qry = 'INSERT INTO model VALUES (NULL, ?, ? ,?, ?)'
        cur.execute(qry, (ivl.chr, interval_id, type, ivl.strand))
        model_id = cur.lastrowid
        if parent_id is not None:
            qry = '''INSERT INTO closure
                SELECT NULL, closure.parent_id, :child_id FROM closure
                WHERE closure.child_id = :parent_id;'''
            # Allows out of order insertion
            #qry = '''INSERT INTO closure
            #    SELECT NULL, p.parent_id, c.child_id FROM closure AS p, closure AS c
            #    WHERE p.child_id = :parent_id AND c.parent_id = :child_id;'''
            cur.execute(qry, {'parent_id': parent_id, 'child_id': model_id})
        qry = 'INSERT INTO closure VALUES (NULL, :model_id, :model_id)'
        cur.execute(qry, locals())
        return model_id
    
    def addIdentifier(self, model_id, value, type='PRIMARY'):
        cur = self.conn.cursor()
        qry = 'SELECT id FROM identifier WHERE model_id = :model_id AND type = :type'
        id = cur.execute(qry, locals()).fetchone()
        qry = 'INSERT INTO identifier VALUES (NULL, :model_id, :value, :type)' if id is None else\
            'UPDATE identifier SET value = :value WHERE model_id = :model_id AND type = :type'
        cur.execute(qry, locals())
        return cur.lastrowid
    
    def getModelById(self, key):
        cur = self.conn.cursor()
        qry = '''SELECT model_id FROM identifier WHERE value = ?'''
        return cur.execute(qry, (name,))
    
        cur = self.conn.cursor()
        qry = '''SELECT model.id, cid.value, model.chr, interval.ivl_fr, interval.ivl_to, model.type, model.strand
            FROM interval, model, closure, identifier AS pid
            LEFT JOIN identifier AS cid ON cid.model_id = model.id
            WHERE
                interval.id = model.interval_id AND
                model.id = closure.child_id AND
                closure.parent_id = pid.model_id AND
                pid.value = ?;
        '''
        rows = cur.execute(qry, (key,))
        res = None
        models = {}
        for model_id, model_name, chm, fr, to, type, strand in rows:
            models[model_id] = Model(model_name, interval(chm, fr, to, strand), type)
            if model_name == key:
                res = models[model_id]
        qry = '''SELECT c.parent_id, c.child_id FROM closure AS p, closure AS c, identifier
            WHERE
                c.child_id = p.child_id AND
                p.parent_id = identifier.model_id AND
                identifier.value = ?;'''
        closure = {v: k for k, v in cur.execute(qry, (key,)) if k != v}
        for child_id, parent_id in closure.iteritems():
            models[parent_id].children.append(models[child_id])
        return res
    
    def getModelsInInterval(self, ivl):
        return []