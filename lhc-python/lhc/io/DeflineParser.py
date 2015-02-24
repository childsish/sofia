import re

# Order deflines by specificity.
DEFLINES = [
	re.compile(r'gb\|(?P<key>\w+)'),
	re.compile(r'gi\|\d+\|emb\|(?P<key>\w+)'),
	re.compile(r'gi\|\d+\|dbj\|(?P<key>\w+)'),
	re.compile(r'pir\|\|(?P<key>\w+)'),
	re.compile(r'prf\|\|(?P<key>\w+)'),
	re.compile(r'sp\|\w*\|(?P<key>\w+)'),
	re.compile(r'pdb\|(?P<key>[^|]+)'),
	re.compile(r'pat\|[^|]+\|(?P<key>\d+)'),
	re.compile(r'bbs\|(?P<key>\d+)'),
	re.compile(r'tpg\|(?P<key>\w+)'),
	re.compile(r'gnl\|[^|]+\|(?P<key>[^. ]+)'),
	re.compile(r'ref\|(?P<key>\w+)'),
	re.compile(r'lcl\|(?P<key>[\w-]+)'),
	re.compile(r'\d+\.[mt]\d+\|(?P<key>LOC_Os\d{2}g\d+)'),
	re.compile(r'CloneID:(?P<key>\w+),CloneLib:\w+'),
	re.compile(r'\((?P<key>\w+)\)'),
	re.compile(r'>(?P<key>\w+)')]

class DeflineParser:
	def __init__(self, deflines = None):
		self.__deflines = deflines
		if deflines == None:
			self.__deflines = DEFLINES
	
	def getAccession(self, defline):
		for regx in self.__deflines:
			match = regx.search(defline)
			if match:
				return match.group('key')
		raise ValueError('No matching regular expressions for "' + defline + '".')
	
	def getHeader(self, defline):
		if defline.split(' ')[0].find('|') == -1:
			return defline
		return defline[defline.find(' ') + 1:]
	
	def getOrganism(self, defline):
		organism = defline[defline.find('['):defline.find(']') + 1]
		if organism == '[imported]':
			organism = defline[defline.find('] - '):-1]
		organism = organism.replace(' ', '_')
		return organism

"""
#genbank1: gi\|(?P<gi>\d+)
genbank2: gb\|(?P<gb>\w+)
embl: gi\|(?P<gi>\d+)\|emb\|(?P<emb>\w+)
ddbj: gi\|(?P<gi>\d+)\|dbj\|(?P<dbj>\w+)
nbrf: pir\|\|(?P<pir>\w+)
prf: prf\|\|(?P<prf>\w+)
swiss-prot: sp\|\w*\|(?P<sp>\w+)
pdb: pdb\|(?P<pdb>[^|]+)
patents: pat\|[^|]+\|(?P<pat>\d+)
geninfo: bbs\|(?P<bbs>\d+)
tpg: tpg\|(?P<tpg>\w+)
tpe: tpe\|(?P<tpe>[^|. ]+)
general: gnl\|(?P<db>[^|]+)\|(?P<gnl>[^. ]+)
reference: ref\|(?P<ref>\w+)
local: lcl\|(?P<lcl>[\w-]+)
tigr: (?P<id>\d+\.[mt]\d+)\|(?P<acc>LOC_Os\d{2}g\d+)
gena: CloneID:(?P<gena>\w+),CloneLib:\w+
rgp: \((?P<rgp>\w+)\)
default: >(?P<def>\w+)

[keywords]
#genbank1: gi
genbank2: gb
embl: emb
ddbj: dbj
nbrf: pir
prf: prf
swiss-prot: sp
pdb: pdb
patents: pat
geninfo: bbs
tpg: tpg
tpe: tpe
general: gnl
reference: ref
local: lcl
tigr: acc
gena: gena
rgp: rgp
default: def
"""