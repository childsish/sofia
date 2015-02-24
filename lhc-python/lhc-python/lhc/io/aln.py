def writeClustal(ents, outfname):
	# Calculate the header padding
	pad = max([len(ent[0]) for ent in ents])
	pad += 7
	
	# Write the data
	outfile = open(outfname, 'w')
	outfile.write('CLUSTAL W (1.81) multiple sequence alignment\n\n')
	for i in xrange(0, len(ents[0][1]), 60):
		f = i
		t = i + 60
		if t > len(ents[0][1]):
			t = len(ents[0][1])
		for hdr, seq in ents:
			outfile.write('>%%-%ds'%pad%hdr)
			outfile.write('%s\n'%(seq[f:t]))
		outfile.write((t-f+pad+1)*' ')
		outfile.write('\n\n')
	outfile.close()

def readClustal(infname):
	ents = {}
	infile = open(infname)
	infile.readline()
	for line in infile:
		if line[0] in ['\n', ' ']:
			continue
		parts = line.split()
		ents.setdefault(parts[0], []).append(parts[1])
	for ent in ents:
		ents[ent] = ''.join(ents[ent])
	return ents.items()
