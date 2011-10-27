from Database import Database
from string import Template

class SNPDatabase(Database):
	def __init__(self, db=':memory:', seqdb=None):
		if seqdb == None:
			raise Exception('No sequence database specified')
		
		Database.__init__(self, db)
		self.accs = {}
		qry = '''SELECT t1.name, t2.acc_id
		 FROM AccessionName AS t1 INNER JOIN AccessionSynonym AS t2
		 ON t1.nam_id = t2.nam_id'''
		for row in self.conn.execute(qry):
			self.accs.setdefault(row[0], []).append(row[1])
		for row in self.conn.execute('''SELECT acc_id FROM Accession'''):
			self.accs.setdefault(row[0], []).append(row[0])
		
		self.conn.execute("ATTACH ? AS seqdb", (seqdb,))
		self.seqs = dict(self.conn.execute('''SELECT name, seq_id FROM
		 seqdb.SequenceSynonym'''))
		self.seq_ids = set()
		for row in self.conn.execute('''SELECT seq_id FROM seqdb.Sequence'''):
			self.seqs[row[0]] = row[0]
			self.seq_ids.add(row[0])
		self.conn.execute('''DETACH seqdb''')
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE Accession (
		 acc_id    INTEGER PRIMARY KEY AUTOINCREMENT,
		 latitute  REAL,
		 longitude REAL,
		 desc      TEXT)''')
		
		self.conn.execute('''CREATE TABLE AccessionName (
		 nam_id INTEGER PRIMARY KEY AUTOINCREMENT,
		 name   TEXT UNIQUE,
		 type   TEXT NOT NULL)''')
		
		self.conn.execute('''CREATE TABLE AccessionSynonym (
		 nam_id INTEGER REFERENCES AccessionName(nam_id),
		 acc_id INTEGER REFERENCES Accession(acc_id))''')
		
		self.conn.execute('''CREATE TABLE SNP (
		 acc_id   INTEGER REFERENCES Accession(acc_id),
		 seq_id   INTEGER UNSIGNED NOT NULL,
		 pos      INTEGER UNSIGNED NOT NULL,
		 snp      TEXT,
		 PRIMARY KEY (acc_id, seq_id, pos))''')
	
	def createIndices(self):
		"""Create the indices on the table."""
		self.conn.execute('''CREATE INDEX IF NOT EXISTS accnam_idx
		 ON AccessionName(name)''')
		self.conn.execute('ANALYZE SNP')
		# Index for SNP(acc_id, seq_id, pos) exists in primary key.
	
	# Register functions
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
	
	def insertSNP(self, acc, seq, pos, snp, typ='name'):
		if len(self.accs[acc]) > 1:
			raise Exception('Accession name is not unique')
		
		acc_id = self.accs[acc][0]
		seq_id = self.seqs[seq]
		
		self.conn.execute('''INSERT INTO SNP VALUES (?, ?, ?, ?)''',
		 (acc_id, seq_id, pos, snp))
	
	def getSNP(self, seq, pos, acc=None):
		tmp = Template('SELECT ${acc1}snp FROM SNP '
		 'WHERE ${acc2}seq_id = ? AND pos == ?')
		args = [self.seqs[seq], pos]
		
		# Insert accessions into query
		if acc == None:
			acc1 = 'acc_id, '
			acc2 = 'acc_id IN (SELECT acc_id FROM Accession) AND '
		elif isinstance(acc, (int, basestring)):
			acc1 = ''
			acc2 = 'acc_id = ? AND '
			args.append(self.__getUniqueAccession(acc))
		elif hasattr(acc, '__iter__'):
			acc1 = 'acc_id, '
			acc2 = 'acc_id IN (%s) AND '%(','.join(len(acc) * ['?']))
			args.extend((self.__getUniqueAccession(a) for a in acc))
		else:
			raise TypeError('Unrecognised accession type: %s'%(str(type(acc)),))
		
		qry = tmp.substitute(acc1=acc1, acc2=acc2)
		res = self.conn.execute(qry, args)
		if isinstance(acc, (int, basestring)):
			res = res.fetchone()
			if res != None:
				res = res[0]
			return res
		return list(res)
	
	def getRange(self, seq, fr=None, to=None, acc=None):
		tmp = Template('SELECT pos${acc1}, snp FROM SNP '
		 'WHERE ${acc2}seq_id = ?${rng} ORDER BY pos${acc1}')
		args = [self.seqs[seq]]
		
		# Insert accessions into query
		if acc == None:
			acc1 = ', acc_id'
			acc2 = 'acc_id IN (SELECT acc_id FROM Accession) AND '
		elif isinstance(acc, (int, basestring)):
			acc1 = ''
			acc2 = 'acc_id = ? AND '
			args.append(self.__getUniqueAccession(acc))
		elif hasattr(acc, '__iter__'):
			acc1 = ', acc_id'
			acc2 = 'acc_id IN (%s) AND '%(','.join(len(acc) * ['?']))
			args.extend((self.__getUniqueAccession(a) for a in acc))
		else:
			raise TypeError('Unrecognised accession type: %s'%(str(type(acc)),))
		
		# Insert range into query
		if fr == None:
			rng = ''
		else:
			rng = ' AND pos BETWEEN ? AND ?'
			args.append(fr)
			args.append(to)
		
		qry = tmp.substitute(rng=rng, acc1=acc1, acc2=acc2)
		print qry
		return list(self.conn.execute(qry, args))
	
	def getPositions(self, seq=None, fr=None, to=None, acc=None):
		tmp = Template('SELECT DISTINCT ${seq_col}pos FROM SNP${where}'\
		 ' ORDER BY ${seq_col}pos')
		args = []
		where = []
		
		# Insert accessions into query
		if acc == None:
			where.append('acc_id IN (SELECT acc_id FROM Accession)')
		elif isinstance(acc, (int, basestring)):
			where.append('acc_id = ?')
			args.append(self.accs[acc][0])
		elif hasattr(acc, '__iter__'):
			where.append('acc_id IN (%s)'%(','.join(len(acc) * ['?']),))
			args.extend((self.__getUniqueAccession(a) for a in acc))
		else:
			raise TypeError('Unrecognised accession type: %s'%(str(type(acc)),))
		
		# Insert sequence into query
		if seq == None:
			where.append('seq_id IN (%s)'%(','.join(map(str, self.seq_ids))))
			seq_col = 'seq_id, '
		elif isinstance(seq, (int, basestring)):
			where.append('seq_id = ?')
			args.append(self.seqs[seq])
			seq_col = ''
		elif hasattr(seq, '__iter__'):
			where.append('seq_id IN (%s)'%(','.join(len(seq) * ['?']),))
			args.extend((self.seqs[s] for s in seq))
			seq_col = 'seq_id, '
		else:
			raise TypeError('Unrecognised sequence type: %s'%(str(type(seq)),))
		
		# Insert range into query
		if fr == None and to == None:
			pass
		elif fr != None and to == None:
			where.append('pos BETWEEN 0 AND ?')
			args.extend((fr,))
		elif fr == None and to != None:
			where.append('pos BETWEEN 0 AND ?')
			args.extend((to,))
		else:
			where.append('pos BETWEEN ? AND ?')
			args.extend((fr, to))
		
		if seq == None and fr == None and to == None and acc == None:
			qry = tmp.substitute(seq_col=seq_col, where='')
			return list((row[0] for row in self.conn.execute(qry)))
		
		qry = tmp.substitute(seq_col=seq_col, where=' WHERE ' + ' AND '.join(where))
		return list((row[0] for row in self.conn.execute(qry, args)))
	
	def __getUniqueAccession(acc):
		if acc not in self.accs:
			raise ValueError('%s has not been registered in this database'%acc)
		elif len(self.accs[acc]) == 0:
			raise ValueError('An error occurred when registering %s'%acc)
		elif len(self.accs[acc]) > 1:
			raise ValueError('%s is not a unique identifier'%acc)
		return self.accs[acc][0]
