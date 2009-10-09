import os
import Bio

from subprocess import Popen, PIPE

class GenBank:
	
	LIBDIR = '/home/childs/lib/GenBank'
	
	def __init__(self, repo=LIBDIR):
		self.seqs = {}
		self.repo = repo
		#self.lastaccess = 0
	
	def __getitem__(self, key):
		return self.seqs[key]
	
	def __setitem__(self, key, value):
		self.seqs[key] = value
	
	#def getFasta
	#def getGBK
	
	def getSeq(self, acc, pwd=None):
		# If we have it already, return it.
		seq = self.__getSeqSelf(acc)
		if seq != '':
			return seq
		
		# Get the sequences and make a local copy
		
		if pwd != None:
			seq = self.__getSeqGrey(acc, pwd)
			if seq != '':
				return seq
		
		return self.__getSeqWeb(acc)
	
	def __getSeqSelf(self, acc):
		accs = os.listdir(self.repo)
		if acc in accs:
			infile = open(os.path.join(self.repo, acc))
			hdr = infile.readline()
			return ''.join([line.strip() for line in infile])
		return ''
	
	def __getSeqGrey(self, acc, pwd):
		prc = Popen(['ssh', 'grey', '~/opt/ncbi-blast-2.2.19+/bin/blastdbcmd -db nt -entry %s'%acc])
		stdout, stderr = prc.communicate(pwd)
		lines = stdout.split('\n')
		if lines[0][0] == '>':
			return ''.join([line.strip() for line in lines[1:]])
		return ''
	
	def __getSeqWeb(self, acc):
		seq = []
		outfile = open(os.path.join(self.repo, acc), 'w')
		# One access per 3 seconds automatically enforced by BioPython
		res = Bio.Entrez.efetch(db='nucleotide', id=acc, rettype='fasta')
		outfile.write(res.readline())
		for line in res:
			outfile.write(line)
			seq.append(line.strip())
		outfile.close()
		res.close()
		
		return ''.join(seq)
