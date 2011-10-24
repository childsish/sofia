from Database import Database

class SequenceDatabase(Database):
	class Sequence:
		def __init__(self, seq_id, curs):
			self.seq_id = seq_id
			self.curs = curs
		
		def __del__(self):
			self.curs.close()
		
		def __str__(self):
			return self.curs.execute('''SELECT seq FROM Sequences WHERE seq_id = ?''',
			 (self.seq_id,)).fetchone()[0]
		
		def __len__(self):
			return self.curs.execute('''SELECT length(seq) FROM Sequences WHERE seq_id = ?''',
			 (self.seq_id,))
		
		def __getitem__(self, key):
			if isinstance(key, int):
				pos = key
				l = 1
			elif isinstance(key, slice):
				pos = key.start
				l = key.stop - key.start
			else:
				raise TypeError('Unrecognised position type: %s'%(type(key),))
			return self.curs.execute('''SELECT substr(seq, ?, ?) FROM Sequences
			 WHERE seq_id = ?''', (pos, l, self.seq_id)).fetchone()[0]
	
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
		
		self.names = dict(self.conn.execute('''SELECT name, seq_id FROM SequenceSynonyms'''))
		for row in self.conn.execute('''SELECT seq_id FROM Sequences'''):
			self.names[row[0]] = row[0]
	
	def __len__(self):
		return len(self.names)
	
	def __getitem__(self, key):
		return SequenceDatabase.Sequence(self.names[key], self.conn.cursor())
	
	def __setitem__(self, key, value):
		self.conn.execute('''UPDATE Sequences SET seq = ? WHERE seq_id = ?''',
		 (value, self.names[key]))
	
	def __delitem__(self, key):
		self.conn.execute('''DELETE FROM Sequences WHERE seq_id = ?''', (self.names[key],))
	
	def __iter__(self):
		return (SequenceDatabase.Sequence(row[0], self.conn.cursor()) for row in
		 self.conn.execute('''SELECT seq_id FROM Sequences'''))
	
	def __contains__(self, key):
		return key in self.names
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Sequences (
		 seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
		 seq    TEXT NOT NULL,
		 desc   TEXT)''')
		
		self.conn.execute('''CREATE TABLE SequenceSynonyms (
		 name   TEXT PRIMARY KEY,
		 seq_id INTEGER REFERENCES Sequences(seq_id))''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX IF NOT EXISTS seqsyn_idx
		 ON SequenceSynonyms(seq_id)''')
	
	def registerSequence(self, name, seq_id=None, seq=None, desc=None):
		if name in self.names:
			return self.names[name]
		
		if seq_id == None:
			# Insert the new sequence and get the seq_id
			self.curs.execute('''INSERT INTO Sequences VALUES (NULL, ?, ?)''', (seq, desc))
			seq_id = self.curs.lastrowid
			
			# seq_id maps to self
			self.names[seq_id] = seq_id
		
		# seq name maps to seq_id
		self.conn.execute('''INSERT INTO SequenceSynonyms VALUES (?, ?)''',
		 (name, seq_id))
		self.names[name] = seq_id
		return seq_id
	
	def registerSequenceSynonyms(self, names, seq=None):
		seq_id = self.registerSequence(names[0], seq=seq)
		for i in xrange(1, len(names)):
			self.registerSequence(names[i], seq_id)
		return seq_id
