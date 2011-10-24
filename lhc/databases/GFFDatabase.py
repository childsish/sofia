from Database import Database

class GFFDatabase(Database):
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Gene (
		 gene_id   TEXT PRIMARY KEY,
		
		self.conn.execute('''CREATE TABLE ''')
		 parent_id INTEGER REFERENCES Annotaion(ann_id),
		 class     TEXT NOT NULL,
		 strand    TEXT CHECK (strand IN ("+", "-")),
		 frame     INTEGER CHECK (frame IN (0, 1, 2)),
		 chm       TEXT NOT NULL,
		 ann_fr    INTEGER UNSIGNED NOT NULL,
		 ann_to    INTEGER UNSIGNED NOT NULL)''')
		self.conn.execute('''CREATE TABLE Description (
		 dsc_id INTEGER PRIMARY KEY AUTOINCREMENT,
		 )''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX idx_mdlpos ON
			Models(chm, mdl_fr, mdl_to)''')
		self.conn.execute('''CREATE INDEX idx_cmppos ON
			Components(chm, cmp_fr, cmp_to)''')
	
	def search(self, key):
		stmt = '''SELECT '''
	
	def getRange(self, chm, fr, to, typ='within'):
		if typ == 'within':
			stmt = '''SELECT mdl_id, strand, class, mdl_fr, mdl_to
			 FROM Models WHERE chm = ? AND mdl_fr > ? AND mdl_to < ?
			 ORDER BY mdl_fr'''
			for row in self.conn.execute(stmt, (chm, fr, to)):
				yield row
		elif typ == 'overlap':
			stmt = '''SELECT mdl_id, strand, class, mdl_fr, mdl_to
			 FROM Models WHERE chm = ? AND
			 ((mdl_fr < ? AND mdl_to > ?) OR (mdl_fr > ? AND mdl_fr < ?))
			 ORDER BY mdl_fr'''
			for row in self.conn.execute(stmt, (chm, fr, fr, fr, to)):
				yield row
		else:
			raise NotImplementedError()
	
	def getModel(self, id_):
		return self.conn.execute('''SELECT id, strand, class, fr, to FROM Models
		 WHERE mdl_id == ?''', (id_,)).fetchone()
	
	def getComponent(self, id_, typ='by_model'):
		if typ == 'by_model':
			stmt = '''SELECT cmp_id, class, cmp_fr, cmp_to FROM
			 Components WHERE mdl_id == ? ORDER BY cmp_fr'''
			for row in self.conn.execute(stmt, (id_,)):
				yield row
		elif typ == 'by_component':
			stmt = '''SELECT mdl_id, class, cmp_fr, cmp_to FROM
			 Components WHERE cmp_id == ?'''
			yield self.conn.execute(stmt, (id_,)).fetchone()
		else:
			raise NotImplementedError()
	
	def insertModel(self, mdl_id, strand, cls, chm, fr, to):
		self.conn.execute('''INSERT INTO Models VALUES (?, ?, ?, ?, ?, ?)''',
		 (mdl_id, strand, cls, chm, fr, to))
	
	def insertComponent(self, mdl_id, cls, chm, fr, to):
		self.conn.execute('''INSERT INTO Components VALUES (NULL, ?, ?, ?, ?, ?)''',
		 (mdl_id, cls, chm, fr, to))
