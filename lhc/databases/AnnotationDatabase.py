from binf.sequence import Range, Complement, Join
from Database import Database

class Gene:
	def __init__(self, ann_id, chm, fr, to, strand, family):
		self.ann_id = ann_id
		self.chm = chm
		self.rng = Range(fr, to)
		if strand == '-':
			self.rng = Complement(self.rng)
		self.strand = strand
		self.family = family
		
		self.mRNA = []
		self.CDS = []
	
	def addmRNA(self, ann_id, fr, to, desc):
		rng = Range(fr, to)
		if self.strand == '-':
			rng = Complement(self.rng)
		self.mRNA.append(mRNA(ann_id, rng, self.strand, desc))
	
	def addCDS(self, cds):
		if self.strand == '-':
			cds = Complement(cds)
		self.CDS.append(cds)

class mRNA:
	def __init__(self, ann_id, rng, strand, desc):
		self.ann_id = ann_id
		self.rng = rng
		self.desc = desc

class AnnotationDatabase(Database):
	def __init__(self, db=':memory:'):
		Database.__init__(self, db)
	
	def createTables(self):
		self.conn.execute('''CREATE TABLE gene (
		 ann_id TEXT PRIMARY KEY,
		 chm    TEXT NOT NULL,
		 ann_fr INTEGER UNSIGNED NOT NULL,
		 ann_to INTEGER UNSIGNED NOT NULL,
		 strand TEXT CHECK (strand IN ("+", "-")),
		 family TEXT)''')
		
		self.conn.execute('''CREATE TABLE mRNA (
		 ann_id TEXT PRIMARY KEY,
		 ann_fr INTEGER UNSIGNED NOT NULL,
		 ann_to INTEGER UNSIGNED NOT NULL,
		 parent TEXT NOT NULL REFERENCES gene(ann_id),
		 desc   TEXT)''')
		
		self.conn.execute('''CREATE TABLE CDS (
		 ann_id INTEGER PRIMARY KEY AUTOINCREMENT,
		 ann_fr INTEGER UNSIGNED NOT NULL,
		 ann_to INTEGER UNSIGNED NOT NULL,
		 parent TEXT REFERENCES mRNA(ann_id))''')
	
	def createIndices(self):
		self.conn.execute('''CREATE INDEX idx_genepos ON
		 gene(chm, ann_fr, ann_to)''')
		self.conn.execute('''CREATE INDEX idx_mRNApos ON
		 mRNA(ann_fr, ann_to)''')
		self.conn.execute('''CREATE INDEX idx_CDSpos ON
		 CDS(ann_fr, ann_to)''')
		self.conn.execute('''CREATE INDEX idx_anndesc ON
		 mRNA(desc)''')
		self.conn.execute('''CREATE INDEX idx_annfam ON
		 gene(family)''')
	
	def insertgene(self, ann_id, chm, fr, to, strand):
		self.conn.execute('INSERT INTO gene VALUES (?, ?, ?, ?, ?, NULL)',
		 (ann_id, chm, fr, to, strand))
	
	def insertmRNA(self, ann_id, fr, to, parent):
		self.conn.execute('INSERT INTO mRNA VALUES (?, ?, ?, ?, NULL)',
		 (ann_id, fr, to, parent))
	
	def insertCDS(self, fr, to, parent):
		self.conn.execute('INSERT INTO CDS VALUES (NULL, ?, ?, ?)',
		 (fr, to, parent))
	
	def setFamily(self, ann_id, family):
		self.conn.execute('UPDATE gene SET family = ? WHERE ann_id = ?',
		 (family, ann_id))
	
	def setDescription(self, ann_id, desc):
		self.conn.execute('UPDATE mRNA SET desc = ? WHERE ann_id = ?',
		 (desc, ann_id))
	
	def getgene(self, ann_id):
		qry = 'SELECT chm, ann_fr, ann_to, strand, family FROM gene '\
		 'WHERE ann_id = ?'
		gene = self.conn.execute(qry, (ann_id,)).fetchone()
		
		gene_obj = Gene(ann_id, gene[0], gene[1], gene[2], gene[3], gene[4])
		qry = 'SELECT ann_id, ann_fr, ann_to, desc FROM mRNA '\
		 'WHERE parent = ?'
		mRNAs = list(self.conn.execute(qry, (ann_id,)))
		for mRNA in mRNAs:
			gene_obj.addmRNA(mRNA[0], mRNA[1], mRNA[2], mRNA[3])
			gene_obj.addCDS(self.getCDS(mRNA[0]))
		return gene_obj
	
	def getCDS(self, ann_id):
		qry = 'SELECT ann_fr, ann_to FROM CDS WHERE parent = ? ORDER BY ann_fr'
		rngs = [Range(fr, to) for fr, to in self.conn.execute(qry, (ann_id,))]
		return Join(rngs)
	
	def getRange(self, chm, fr, to):
		qry = 'SELECT ann_id FROM gene WHERE chm = ? AND ann_fr > ? AND ann_to < ?'
		return [self.getgene(row[0]) for row in self.conn.execute(qry, (chm, fr, to))]
	
	def searchAnnotation(self, term):
		qry = 'SELECT parent FROM mRNA WHERE desc LIKE ?'
		return [self.getgene(row[0]) for row in self.conn.execute(qry, ('%%%s%%'%(term,)))]
