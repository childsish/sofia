from numpy import log2

aa_alphabet = {'A': 0.0, 'C': 0.0, 'D': 0.0, 'E': 0.0,
               'F': 0.0, 'G': 0.0, 'H': 0.0, 'I': 0.0,
               'K': 0.0, 'L': 0.0, 'M': 0.0, 'N': 0.0,
               'P': 0.0, 'Q': 0.0, 'R': 0.0, 'S': 0.0,
               'T': 0.0, 'V': 0.0, 'W': 0.0, 'Y': 0.0}
na_alphabet = {'A': 0.0, 'C': 0.0, 'G': 0.0, 'T': 0.0}
ra_alphabet = {'A': 0.0, 'C': 0.0, 'G': 0.0, 'U': 0.0}

class ALNFile(dict):
	
	CONSENSUS = 'consensus'
	
	def __init__(self, filename, format='clustalw'):
		self.order = []
		
		if format == 'clustalw':
			self.__parseClustal(filename)
		elif format == 'fasta':
			self.__parseFasta(filename)
		else:
			raise ArgumentError("Unrecognised format: " + str(format))
	
	def getHeight(self):
		return len(self)
	
	def getLength(self):
		return len(self.values()[0])
	
	def getInformationContent(self, alphabet = aa_alphabet):
		aln = self.values()
		res = []
		i = 0
		
		while i < self.getLength():
			f = alphabet.copy()
			j = 0
			while j < self.getHeight():
				if aln[j][i] in f:
					f[aln[j][i]] += 1.0
				j += 1
			sum = 0.0
			total = float(self.getHeight())
			for v in f.values():
				if v == 0:
					continue
				sum += (v/total) * log2(v/total)
			res.append(log2(self.getHeight()) + sum)
			i += 1
		return res
	
	def __parseClustal(self, filename):
		infile = file(filename)
		infile.readline()
		idx = 0
		for line in infile:
			if len(line) == 1:
				continue
			
			if idx == 0:
				idx = line.rfind(' ') + 1
			
			key = line[:idx]
			if key == idx * ' ':
				key = ALNFile.CONSENSUS
			key = key.strip()
			if not key in self.order:
				self.order.append(key)
			self.setdefault(key, '')
			self[key] += line[idx:-1]
		infile.close()
		
		self.__length = len(self.values()[0])
	
	def __parseFasta(self, filename):
		infile = file(filename)
		lines = infile.readlines()
		infile.close()
		
		for i in xrange(0, len(lines), 2):
			key = lines[i][1:lines[i].find(' ')]
			self.order.append(key)
			self[key] = lines[i+1]
