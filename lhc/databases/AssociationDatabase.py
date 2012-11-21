from Database import Database

class AssociationDatabase(Database):
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
		
		self.trts = set((row[0] for row in
		 self.conn.execute('SELECT DISTINCT trait FROM Association')))
		self.chms = set((row[0] for row in
		 self.conn.execute('SELECT DISTINCT chm FROM Association')))
		self.poss = set((row[0] for row in
		 self.conn.execute('SELECT DISTINCT pos FROM Association')))
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Association (
		 trait  TEXT NOT NULL,
		 chm    TEXT NOT NULL,
		 pos    INTEGER UNSIGNED NOT NULL,
		 lod    REAL NOT NULL)''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX IF NOT EXISTS ass_idx ON Association
		 (trait, chm, pos)''')
	
	def getPosition(self, trt, chm, pos):
		if trt not in self.trts:
			raise Exception('Invalid trait: %s'%trt)
		elif chm not in self.chms:
			raise Exception('Invalid chromosome: %s'%chm)
		elif pos not in self.poss:
			raise Exception('Invalid position: %d'%pos)
		qry = 'SELECT lod FROM Association WHERE trait = ? AND chm = ? and pos = ?'
		res = self.conn.execute(qry, (trt, chm, pos)).fetchone()
		if res == None:
			raise Exception('Invalid association')
		return res[0]
	
	def getRange(self, trt, chm, fr, to):
		stmt = '''SELECT pos, lod FROM Association WHERE trait = ? AND chm = ? AND
		 pos BETWEEN ? AND ? ORDER BY pos'''
		for row in self.conn.execute(stmt, (trt, chm, fr, to)):
			yield row
	
	def insertValue(self, trait, chm, pos, val):
		self.conn.execute('''INSERT INTO Association VALUES (?, ?, ?, ?)''',
		 (trait, chm, pos, val))
	
	def insertValues(self, vals):
		self.conn.executemany('''INSERT INTO Association VALUES (?, ?, ?, ?)''', vals)

def iterFile(infname):
	infile = open(infname)
	infile.readline()
	for line in infile:
		parts = line.split('\t')
		yield (parts[1], int(parts[2]), float(parts[3]))
	infile.close()

def updateDatabase(fname, dbname):
	db = AssociationDatabase(dbname)
	db.insertValues(iterFile(fname))

def main(argv):
	updateDatabase(argv[1], argv[2])
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
