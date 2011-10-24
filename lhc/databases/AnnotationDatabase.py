from Database import Database

class AnnotationDatabase(Database):
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Annotation (
		 ann_id TEXT PRIMARY KEY,
		 chm    TEXT NOT NULL,
		 ann_fr INTEGER UNSIGNED NOT NULL,
		 ann_to INTEGER UNSIGNED NOT NULL,
		 desc   TEXT,
		 family TEXT)''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX idx_annpos ON
		 Annotation(chm, ann_fr, ann_to)''')
		self.conn.execute('''CREATE INDEX idx_anndesc ON
		 Annotation(desc)''')
		self.conn.execute('''CREATE INDEX idx_annfam ON
		 Annotation(family)''')
	
	def insertAnnotation(self, ann_id, chm, fr, to):
		self.conn.execute('''INSERT INTO Annotation VALUES (?, ?, ?, ?, NULL, NULL)''',
		 (ann_id, chm, fr, to))
	
	def updateColumn(self, ann_id, **kw):
		for key, val in kw.iteritems():
			self.conn.execute('UPDATE Annotation SET %s = ? WHERE ann_id = ?'%(key,),\
			 (val, ann_id))
	
	def getRange(self, chm, fr, to, typ='within'):
		if typ == 'within':
			stmt = '''SELECT ann_id, ann_fr, ann_to, desc
			 FROM Annotation WHERE chm = ? AND ann_fr > ? AND ann_to < ?
			 ORDER BY ann_fr'''
			for row in self.conn.execute(stmt, (chm, fr, to)):
				yield row
		elif typ == 'overlap':
			stmt = '''SELECT ann_id, ann_fr, ann_to, desc
			 FROM Models WHERE chm = ? AND
			 ((? BETWEEN ann_fr AND ann_to) OR (ann_fr > ? AND ann_fr < ?))
			 ORDER BY ann_fr'''
			for row in self.conn.execute(stmt, (chm, fr, fr, to)):
				yield row
		else:
			raise NotImplementedError()
	
	def getAnnotation(self, ann_id):
		return self.conn.execute('''SELECT ann_fr, ann_to, desc FROM Annotation
		 WHERE ann_id == ?''', (ann_id,)).fetchone()
	
	def searchAnnotation(self, term):
		return self.conn.execute('SELECT ann_id, chm, ann_fr, ann_to FROM Annotation '\
		 'WHERE desc LIKE ?', ('%%%s%%'%(term,),))
