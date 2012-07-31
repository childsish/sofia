from Database import Database

class SequenceDatabase(Database):
	
	SEGMENT_SIZE = 10000
	
	class Sequence(object):
		def __init__(self, seq_id, curs):
			self.seq_id = seq_id
			self.curs = curs
		
		def __del__(self):
			self.curs.close()
		
		def __str__(self):
			return ''.join(row[0] for row in self.curs.execute('''SELECT seq
			 FROM SequenceSegment WHERE seq_id = ? ORDER BY idx''', (self.seq_id,)))
		
		def __len__(self):
			idx, l = self.curs.execute('''SELECT idx, length(seq) FROM SequenceSegment
			 WHERE seq_id = ? AND idx = (SELECT max(idx) FROM SequenceSegment
			 WHERE seq_id = ?)''',
			 (self.seq_id, self.seq_id)).fetchone()
			return idx * SequenceDatabase.SEGMENT_SIZE + l
		
		def __getitem__(self, key):
			if isinstance(key, int):
				fr = key
				to = key + 1
			elif isinstance(key, slice):
				fr = key.start
				to = key.stop
			elif hasattr(key, '__iter__'):
				raise NotImplementedError()
			else:
				raise TypeError('Unrecognised position type: %s'%(type(key),))
			
			seg_sz = SequenceDatabase.SEGMENT_SIZE
			seq = ''.join((row[0] for row in self.curs.execute('''SELECT seq
			 FROM SequenceSegment WHERE seq_id = ? AND idx BETWEEN ? AND ?''',
			 (self.seq_id, fr / seg_sz, to / seg_sz))))
			return seq[fr%seg_sz:to - fr + (fr%seg_sz)]
		
		def registerDescription(self, desc):
			self.curs.execute('''UPDATE Sequence SET desc = ? WHERE seq_id = ?''',
			 (self.seq_id, desc))
	
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
		
		self.names = dict(self.conn.execute('''SELECT name, seq_id FROM SequenceSynonym'''))
		for row in self.conn.execute('''SELECT seq_id FROM Sequence'''):
			self.names[row[0]] = row[0]
	
	def __str__(self):
		res = []
		for seq_id in self:
			print seq_id
			nseg = self.conn.execute('''SELECT max(idx) FROM SequenceSegment
			 WHERE seq_id = ?''', (seq_id,)).fetchone()[0]
			seq = self.conn.execute('''SELECT seq FROM SequenceSegment
			 WHERE seq_id = ? AND idx = 0''', (seq_id,)).fetchone()[0]
			if len(seq) < SequenceDatabase.SEGMENT_SIZE:
				seq += '...'
			res.append('%d\t%d\t%s'%(seq_id, nseg, seq))
		return '\n'.join(res)
	
	def __len__(self):
		return len(self.names)
	
	def __getitem__(self, key):
		return SequenceDatabase.Sequence(self.names[key], self.conn.cursor())
	
	def __setitem__(self, key, value):
		if key not in self.names:
			self.curs.execute('''INSERT INTO Sequence VALUES (NULL, "")''')
			seq_id = self.curs.lastrowid
			self.conn.execute('''INSERT INTO SequenceSynonym VALUES (?, ?)''',
			 (key, seq_id))
			self.names[key] = seq_id
		else:
			seq_id = self.names[key]
			self.conn.execute('''DELETE FROM SequenceSegment WHERE seq_id == ?''', (seq_id,))
		
		seg_sz = SequenceDatabase.SEGMENT_SIZE
		self.conn.executemany('''INSERT INTO SequenceSegment VALUES (?, ?, ?)''',
		 ((seq_id, i, value[i * seg_sz:(i + 1) * seg_sz])
		 for i in xrange((len(value) / seg_sz) + (len(value)%seg_sz > 0))))
	
	def __delitem__(self, key):
		seq_id = self.names[key]
		self.conn.execute('''DELETE FROM SequenceSegment WHERE seq_id == ?''', (seq_id,))
		self.conn.execute('''DELETE FROM Sequence WHERE seq_id = ?''', (seq_id,))
	
	def __iter__(self):
		return (row[0] for row in
		 self.conn.cursor().execute('''SELECT seq_id FROM Sequence'''))
	
	def __contains__(self, key):
		return key in self.names
	
	def iteritems(self):
		raise NotImplementedError()
	
	def iterkeys(self):
		raise NotImplementedError()
	
	def itervalues(self):
		raise NotImplementedError()
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Sequence (
		 seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
		 desc   TEXT NOT NULL)''')
		
		self.conn.execute('''CREATE TABLE SequenceSegment (
		 seq_id INTEGER REFERENCES Sequence(seq_id),
		 idx    INTEGER NOT NULL,
		 seq    TEXT NOT NULL)''')
		
		self.conn.execute('''CREATE TABLE SequenceSynonym (
		 name   TEXT PRIMARY KEY,
		 seq_id INTEGER REFERENCES Sequence(seq_id))''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX IF NOT EXISTS seqsyn_idx
		 ON SequenceSynonym(seq_id)''')
		self.conn.execute('''CREATE INDEX IF NOT EXISTS seqseg_idx
		 ON SequenceSegment(seq_id, idx)''')
	
	def registerDescription(self, key, desc):
		seq_id = self.names[key]
		self.conn.execute('''UPDATE Sequence SET desc = ? WHERE seq_id = ?''', (seq_id, desc))
	
	def registerSequenceSynonym(self, names, seq=None):
		seq_id = self.registerSequence(names[0], seq=seq)
		for i in xrange(1, len(names)):
			self.registerSequence(names[i], seq_id)
		return seq_id

def main():
	db = SequenceDatabase()
	SequenceDatabase.SEGMENT_SIZE = 20
	
	seq = 'aaaaacccccgggggtttttAAAAACCCCCGGGGGTTTTTaaaaacccccgggggttttt'\
	'111222333444555666777888999000'
	db['Test'] = seq
	for i in [4, 5, 19, 20, 21, 39, 40, 41, 59, 60, 61, len(seq) - 1]:
		print db['Test'][i] == seq[i]
	print len(seq) == len(db['Test'])

if __name__ == '__main__':
	main()
