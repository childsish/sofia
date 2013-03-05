def iterGff(fname):
    infile = open(fname)
    for line in infile:
        seq, src, typ, fr, to, scr, strand, phase, attr =\
            line.strip().split('\t')
        fr, to = int(fr) - 1, int(to)
        yield seq, src, typ, fr, to, scr, strand, phase, attr
    infile.close()
