import os
import sys

MINSTEM = 3

def getHairpins(fname):
	infile = open(fname)
	rec = False
	ctrs = {}
	for line in infile:
		if line.startswith('showpage'):
			rec = False
		
		if rec:
			xi, xj, prb, ubox = line.split()
			xi = int(xi)
			xj = int(xj)
			ctr = (xi + xj) / 2.
			ctrs.setdefault(ctr, []).append((xi, xj))
		
		if line.startswith('drawgrid_turn'):
			rec = True
	infile.close()
	
	res = []
	for k, vs in sorted(ctrs.iteritems()):
		run = [vs[-1]]
		for i in xrange(2, len(vs)+1):
			if vs[-i][0] + 1 == run[-1][0]:
				run.append(vs[-i])
			elif len(run) >= MINSTEM:
				res.append((k, run[-1][1] - run[-1][0] - 2*len(run), len(run)))
				run = [vs[-i]]
			else:
				run = [vs[-i]]
		
		if len(run) >= MINSTEM:
			res.append((k, run[-1][1] - run[-1][0] - 2*len(run), len(run)))
	return res

def getSequence(fname):
	res = []
	rec = False
	infile = open(fname)
	for line in infile:
		if line.startswith('/sequence'):
			rec = True
		
		if rec:
			res.append(line.strip())
			if line.strip().endswith('def'):
				break
	return ''.join(res)[13:-7]

def main(argv):
	indir = '../../data/bpp'
	sys.stdout.write('hdr\txi\txj\tlen\n')
	for fname in os.listdir(indir):
		if not fname.endswith('.ps'):
			continue
		
		hpns = getHairpins(os.path.join(indir, fname))
		for hpn in hpns:
			sys.stdout.write(fname[:-6])
			sys.stdout.write('\t%.1f\t%d\t%d\n'%hpn)

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
