from Database import Database

class SNPDatabase(Database):
	
	SEGMENT_SIZE = 2000
	
	class Sequence(object):
		def __init__(self, acc_id, curs):
			self.acc_id = acc_id
			self.curs = curs
		
		def __del__(self):
			self.curs.close()
		
		def __str__(self):
			return ''.join(row[0] for row in self.curs.execute('''SELECT seq
			 FROM SequenceSegment WHERE acc_id = ? ORDER BY idx''', (self.acc_id,)))
		
		def __len__(self):
			idx, l = self.curs.execute('''SELECT idx, length(seq) FROM SequenceSegment
			 WHERE acc_id = ? AND idx = (SELECT max(idx) FROM SequenceSegment
			 WHERE acc_id = ?)''',
			 (self.acc_id, self.acc_id)).fetchone()
			return idx * SNPDatabase.SEGMENT_SIZE + l
		
		def __getitem__(self, key):
			if isinstance(key, int):
				fr = key
				to = key + 1
			elif isinstance(key, slice):
				fr = key.start
				to = key.stop
				if fr == None:
					fr = 0
				if to == None:
					to = len(self)
			elif hasattr(key, '__iter__'):
				raise NotImplementedError()
			else:
				raise TypeError('Unrecognised position type: %s'%(type(key),))
			
			seg_sz = SNPDatabase.SEGMENT_SIZE
			seq = ''.join((row[0] for row in self.curs.execute('''SELECT seq
			 FROM SequenceSegment WHERE acc_id = ? AND idx BETWEEN ? AND ?''',
			 (self.acc_id, fr / seg_sz, to / seg_sz))))
			return seq[fr%seg_sz:to - fr + (fr%seg_sz)]
		
		def __iter__(self):
			qry = 'SELECT idx FROM SequenceSegment WHERE acc_id = ? ORDER BY idx'
			idxs = list(row[0] for row in self.curs.execute(qry, (self.acc_id,)))
			qry = 'SELECT seq FROM SequenceSegment WHERE acc_id = ? AND idx = ?'
			for idx in idxs:
				seg = self.curs.execute(qry, (self.acc_id, idx)).fetchone()[0]
				for char in seg:
					yield char
		
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
		self.accs = {}
		self.acc_ids = set()
		qry = '''SELECT t1.name, t2.acc_id
		 FROM AccessionName AS t1 INNER JOIN AccessionSynonym AS t2
		 ON t1.nam_id = t2.nam_id'''
		for row in self.conn.execute(qry):
			self.accs.setdefault(row[0], []).append(row[1])
		for row in self.conn.execute('''SELECT acc_id FROM Accession'''):
			self.accs.setdefault(row[0], []).append(row[0])
			self.acc_ids.add(row[0])
	
	def __str__(self):
		res = []
		for acc_id in self:
			print acc_id
			nseg = self.conn.execute('''SELECT max(idx) FROM SequenceSegment
			 WHERE acc_id = ?''', (acc_id,)).fetchone()[0]
			seq = self.conn.execute('''SELECT seq FROM SequenceSegment
			 WHERE acc_id = ? AND idx = 0''', (acc_id,)).fetchone()[0]
			if len(seq) < SNPDatabase.SEGMENT_SIZE:
				seq += '...'
			res.append('%d\t%d\t%s'%(acc_id, nseg, seq))
		return '\n'.join(res)
	
	def __len__(self):
		return len(self.accs)
	
	def __getitem__(self, key):
		acc_id = self.__getUniqueAccession(key)
		return SNPDatabase.Sequence(acc_id, self.conn.cursor())
	
	def __setitem__(self, key, value):
		acc_id = self.__getUniqueAccession(key)
		
		self.conn.execute('''DELETE FROM SequenceSegment WHERE acc_id == ?''', (acc_id,))
		
		seg_sz = SNPDatabase.SEGMENT_SIZE
		self.conn.executemany('''INSERT INTO SequenceSegment VALUES (?, ?, ?)''',
		 ((acc_id, i, value[i * seg_sz:(i + 1) * seg_sz])
		 for i in xrange((len(value) / seg_sz) + (len(value)%seg_sz > 0))))
	
	def __iter__(self):
		return (row[0] for row in
		 self.conn.cursor().execute('''SELECT acc_id FROM Accession'''))
	
	def __contains__(self, key):
		return key in self.accs
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Accession (
		 acc_id    INTEGER PRIMARY KEY AUTOINCREMENT,
		 latitude  REAL,
		 longitude REAL,
		 desc      TEXT)''')
		
		self.conn.execute('''CREATE TABLE AccessionName (
		 nam_id INTEGER PRIMARY KEY AUTOINCREMENT,
		 name   TEXT UNIQUE,
		 type   TEXT NOT NULL)''')
		
		self.conn.execute('''CREATE TABLE AccessionSynonym (
		 nam_id INTEGER REFERENCES AccessionName(nam_id),
		 acc_id INTEGER REFERENCES Accession(acc_id))''')
		
		self.conn.execute('''CREATE TABLE SequenceSegment (
		 acc_id INTEGER REFERENCES Accession(acc_id),
		 idx    INTEGER NOT NULL,
		 seq    TEXT NOT NULL)''')
		
		self.conn.execute('''CREATE TABLE Position (
		 pos_id  INTEGER PRIMARY KEY AUTOINCREMENT,
		 chm  TEXT NOT NULL,
		 pos     INTEGER NOT NULL)''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX IF NOT EXISTS accname_idx
		 ON AccessionName(name)''')
		self.conn.execute('''CREATE INDEX IF NOT EXISTS seqseg_idx
		 ON SequenceSegment(acc_id, idx)''')
		self.conn.execute('''CREATE INDEX IF NOT EXISTS pospos_idx
		 ON Position(chm, pos)''')
	
	def registerAccession(self, lat=None, lon=None, desc=None):
		# Insert the new accession and get the acc_id
		self.curs.execute("INSERT INTO Accession VALUES (NULL, ?, ?, ?)", (lat, lon, desc))
		acc_id = self.curs.lastrowid
		self.accs[acc_id] = [acc_id]
		return acc_id

	def registerAccessionSynonym(self, acc, typ, acc_id):
		# Check if accession exists
		if acc_id not in self.accs:
			raise Exception('Accession does not exist in database')
		
		# Insert name and link
		if acc not in self.accs:
			self.curs.execute("INSERT INTO AccessionName VALUES (NULL, ?, ?)", (acc, typ))
			nam_id = self.curs.lastrowid
		else:
			nam_id = self.curs.execute("SELECT nam_id FROM AccessionName WHERE name = ?",
			 (acc,)).fetchone()[0]
		self.curs.execute("INSERT INTO AccessionSynonym VALUES (?, ?)", (nam_id, acc_id))
		
		# Update python object
		self.accs.setdefault(acc, []).append(acc_id)
		return nam_id
	
	def addPosition(self, chm, pos):
		qry = 'INSERT INTO Position VALUES (NULL, ?, ?)'
		self.execute(qry, (chm, pos))

	def iterPositions(self, accs=None):
		qry = 'SELECT pos_id, chm, pos FROM Position'
		#if accs == None:
		for pos_id, chm, pos in self.conn.execute(qry):
			yield pos_id - 1, chm, pos
		
		#for pos_id, chm, pos in self.conn.execute(qry):
		#	ales = set(self[acc][pos_id - 1] for acc in accs)
		#	if len(ales - {'X', 'N', '-'}) > 2:
		#		yield pos_id - 1, chm, pos
	
	def __getUniqueAccession(self, acc):
		if acc not in self.accs:
			raise ValueError('%s has not been registered in this database'%acc)
		elif len(self.accs[acc]) == 0:
			raise ValueError('An error occurred when registering %s'%acc)
		elif len(self.accs[acc]) > 1:
			raise ValueError('%s is not a unique identifier'%acc)
		return self.accs[acc][0]
	
def main():
	db = SNPDatabase()
	SNPDatabase.SEGMENT_SIZE = 20
	
	seq = 'aaaaacccccgggggtttttAAAAACCCCCGGGGGTTTTTaaaaacccccgggggttttt'\
	'111222333444555666777888999000'
	db['Test'] = seq
	for i in [4, 5, 19, 20, 21, 39, 40, 41, 59, 60, 61, len(seq) - 1]:
		print db['Test'][i] == seq[i]
	print len(seq) == len(db['Test'])

if __name__ == '__main__':
	main()
