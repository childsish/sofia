'''
Created on 05/08/2013

@author: Liam Childs
'''

import sqlite3

from collections import defaultdict
from lhc.binf.genomic_interval import interval
from lhc.collection.nested_containment_list import NestedContainmentList as NCList

class Model(object):
    
    def __init__(self, name, ivl, type):
        self.name = name
        self.ivl = ivl
        self.type = type
        self.children = []

class ModelSet(object):
    
    def __init__(self, fname, mode='r'):
        base = fname.rsplit('.', 1)[0]
        db_name = fname if fname == ':memory:' else '%s.db'%base
        nc_name = '%s.nc'%base
        self.conn = sqlite3.connect(db_name)
        self.ncl = NCList(nc_name, mode, diskless=fname == ':memory:')
        self.ivls = []
        if mode == 'w':
            self.createTables()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.commit()
            self.conn.close()
    
    def __getitem__(self, key):
        ''' Warning. Requires in-order insertion of segments. '''
        if isinstance(key, basestring):
            return self.getModelById(key)
        elif isinstance(key, interval):
            return self.getModelsInInterval(key)
        raise TypeError('Unknown type used to get gene models: %s'%type(key))
    
    def createTables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chr TEXT,
            interval_id INTEGER,
            type TEXT,
            strand TEXT
        );''')
        cur.execute('''CREATE TABLE IF NOT EXISTS closure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER REFERENCES model(id),
            child_id INTEGER REFERENCES model(id)
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS identifier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER REFERENCES model(id),
            value TEXT,
            type TEXT
        );''')
    
    def addModelSegment(self, ivl, type, parent_id=None):
        ''' Warning. Requires in order insertion of segments. '''
        cur = self.conn.cursor()
        self.ivls.append(ivl)
        qry = 'INSERT INTO model VALUES (NULL, ?, NULL ,?, ?)'
        cur.execute(qry, (ivl.chr, type, ivl.strand))
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
    
    def finaliseIntervals(self):
        cur = self.conn.cursor()
        ivl_map = self.ncl.insertIntervals(self.ivls)
        qry = 'UPDATE model SET interval_id = :interval_id WHERE id = :id'
        cur.executemany(qry, ({'id': id + 1, 'interval_id': int(interval_id)}\
            for id, interval_id in enumerate(ivl_map)))
    
    def addIdentifier(self, model_id, value, type='PRIMARY'):
        cur = self.conn.cursor()
        qry = 'SELECT id FROM identifier WHERE model_id = :model_id AND type = :type'
        id = cur.execute(qry, locals()).fetchone()
        qry = 'INSERT INTO identifier VALUES (NULL, :model_id, :value, :type)' if id is None else\
            'UPDATE identifier SET value = :value WHERE model_id = :model_id AND type = :type'
        cur.execute(qry, locals())
        return cur.lastrowid
    
    def getModelById(self, key):
        #cur = self.conn.cursor()
        #qry = '''SELECT model_id FROM identifier WHERE value = ?'''
        #return cur.execute(qry, (key,))
    
        cur = self.conn.cursor()
        qry = '''SELECT model.id, cid.value, model.chr, model.interval_id, model.type, model.strand
            FROM model, closure, identifier AS pid
            LEFT JOIN identifier AS cid ON cid.model_id = model.id
            WHERE
                model.id = closure.child_id AND
                closure.parent_id = pid.model_id AND
                pid.value = ?;
        '''
        rows = cur.execute(qry, (key,))
        res = None
        models = {}
        for model_id, model_name, chm, interval_id, type, strand in rows:
            ivl = self.ncl[interval_id]
            models[model_id] = Model(model_name, interval(chm, ivl.start, ivl.stop, strand), type)
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
