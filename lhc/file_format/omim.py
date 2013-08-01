def iterOmim(fname):
    infile = open(fname)
    infile.readline()
    c_field = None
    rec = {}
    for line in infile:
        if line.startswith('*RECORD*'):
            for k in rec:
                rec[k] = ''.join(rec[k]).strip()
            yield rec['NO'], rec
            rec = {}
        elif line.startswith('*FIELD*'):
            c_field = line.strip().split()[1]
            rec[c_field] = []
        else:
            rec[c_field].append(line)
    infile.close()
