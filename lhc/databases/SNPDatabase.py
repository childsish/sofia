from Database import Database
from string import Template

class SNPDatabase(Database):
	def __init__(self, db=':memory:', seqdb=None):
		if seqdb == None:
			raise Exception('No sequence database specified')
		
		Database.__init__(self, db)
		self.accs = dict(self.conn.execute('''SELECT name, acc_id FROM
		 AccessionSynonyms'''))
		for row in self.conn.execute('''SELECT acc_id FROM Accessions'''):
			self.accs[row[0]] = row[0]
		
		self.conn.execute('''ATTACH ? AS seqdb''', (seqdb,))
		self.seqs = dict(self.conn.execute('''SELECT name, seq_id FROM
		 seqdb.SequenceSynonyms'''))
		for row in self.conn.execute('''SELECT seq_id FROM seqdb.Sequences'''):
			self.seqs[row[0]] = row[0]
		self.conn.execute('''DETACH seqdb''')
		
		self.poss = dict(((acc_id, None) for acc_id in self.accs.itervalues()))
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Accessions (
		 acc_id    INTEGER PRIMARY KEY AUTOINCREMENT,
		 latitute  REAL,
		 longitude REAL,
		 desc      TEXT)''')
		
		self.conn.execute('''CREATE TABLE AccessionSynonyms (
		 name   TEXT PRIMARY KEY,
		 acc_id INTEGER REFERENCES Accessions(acc_id))''')
		
		self.conn.execute('''CREATE TABLE SNPs (
		 acc_id   INTEGER REFERENCES Accessions(acc_id),
		 seq_id   INTEGER UNSIGNED NOT NULL,
		 pos      INTEGER UNSIGNED NOT NULL,
		 snp      TEXT NOT NULL,
		 PRIMARY KEY (acc_id, seq_id, pos))''')
	
	def createIndices(self):
		"""Create the indices on the table."""
		self.conn.execute('''CREATE INDEX IF NOT EXISTS accsyn_idx
		 ON AccessionSynonyms(acc_id)''')
	
	# Register functions
	def registerAccession(self, acc, acc_id=None, lat=None, lon=None, desc=None):
		if acc in self.accs:
			return self.accs[acc]
		
		if acc_id == None:
			# Insert the new accession and get the acc_id
			self.curs.execute('''INSERT INTO Accessions VALUES (NULL, ?, ?, ?)''',
			 (lat, lon, desc))
			acc_id = self.curs.lastrowid
			
			# acc_id maps to self
			self.accs[acc_id] = acc_id
		
		# acc name maps to acc_id
		self.conn.execute('''INSERT INTO AccessionSynonyms VALUES (?, ?)''',
		 (acc, acc_id))
		self.accs[acc] = acc_id
		return acc_id
	
	def registerAccessionSynonyms(self, accs, lat=None, lon=None, desc=None):
		acc_id = self.registerAccession(accs[0], None, lat, lon, desc)
		for i in xrange(1, len(accs)):
			self.registerAccession(accs[i], acc_id)
		return acc_id
	
	def insertSNP(self, acc, seq, pos, snp):
		acc_id = self.registerAccession(acc)
		seq_id = self.seqs[seq]
		
		self.conn.execute('''INSERT INTO SNPs VALUES (?, ?, ?, ?)''',
		 (acc_id, seq_id, pos, snp))
	
	def getSNP(self, acc, chm, pos):
		acc_id = self.accs[acc]
		seq_id = self.seqs[seq]
		
		snp = self.conn.execute('''SELECT snp FROM SNPs WHERE acc_id = ? AND seq_id = ?
		 AND pos = ?''', (acc_id, seq_id, pos)).fetchone()
		if snp != None:
			snp = snp[0]
		return snp
	
	def getRange(self, seq, fr=None, to=None, accs=None):
		tmp = Template('SELECT ${acc1}pos, snp FROM SNPs '
		 'WHERE seq_id = ?${rng}${acc2} ORDER BY ${acc3}pos')
		args = [self.seqs[seq]]
		
		# Insert range into query
		if fr == None:
			rng = ''
		else:
			rng = ' AND pos BETWEEN ? AND ?'
			args.append(fr)
			args.append(to)
		
		# Insert accessions into query
		if accs == None:
			acc1 = 'acc_id, '
			acc2 = ''
		elif type(accs) in (int, basestring):
			acc1 = ''
			acc2 = ' AND acc_id = ?'
			args.append(self.accs[acc])
		elif hasattr(accs, '__iter__'):
			acc1 = 'acc_id, '
			acc2 = ' AND acc_id IN (%s)'%(','.join(len(accs) * ['?']))
			args.extend((self.accs[acc] for acc in accs))
		else:
			raise TypeError('Unrecognised accession type: %s'%(str(type(accs)),))
		
		qry = tmp.substitute(rng=rng, acc1=acc1, acc2=acc2, acc3=acc1)
		return list(self.conn.execute(qry, args))
	
	def getPositions(self, seq, fr=None, to=None, accs=None):
		tmp = Template('''SELECT DISTINCT pos FROM SNPs WHERE seq_id == ?${rng}${acc}
		 ORDER BY pos''')
		args = [self.seqs[seq]]
		
		# Insert range into query
		if fr == None:
			rng = ''
		elif fr != None:
			rng = ' AND pos BETWEEN ? AND ?'
			args.extend((fr, to))
		
		# Insert accessions into query
		if accs == None:
			acc = ''
		elif type(accs) in (int, basestring):
			acc = ' AND acc_id == ?'
			args.append(self.accs[acc])
		elif hasattr(accs, '__iter__'):
			acc = ' AND acc_id IN (%s)'%(','.join(len(accs) * ['?']))
			args.extend((self.accs[acc] for acc in accs))
		else:
			raise TypeError('Unrecognised accession type: %s'%(str(type(accs)),))
		
		qry = tmp.substitute(rng=rng, acc=acc)
		return list((row[0] for row in self.conn.execute(qry, args)))
