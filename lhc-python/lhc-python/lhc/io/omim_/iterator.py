import gzip

class OmimIterator(object):
    def __init__(self, fname):
        self.fname = fname

    def __iter__(self):
        fhndl = gzip.open(self.fname) if self.fname.endswith('.gz') else\
            open(self.fname)
        fhndl.readline()
        c_field = None
        rec = {}
        for line in fhndl:
            if line.startswith('*RECORD*'):
                for k in rec:
                    rec[k] = re.sub('(?<!\n)\n(?!\n)', ' ',
                        ''.join(rec[k]).strip())
                yield rec
                rec = {}
            elif line.startswith('*FIELD*'):
                c_field = line.strip().split()[1]
                rec[c_field] = []
            else:
                rec[c_field].append(line)
        fhndl.close()

