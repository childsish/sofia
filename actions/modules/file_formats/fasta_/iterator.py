import gzip

from collections import namedtuple

FastaEntry = namedtuple('FastaEntry', ('hdr', 'seq'))


class FastaIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = gzip.open(fname) if fname.endswith('.gz') else open(fname)
        
        self.hdr = self.fhndl.next().strip().split()[0][1:]
        self.seq = []
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.hdr is None:
            raise StopIteration()
        res = None
        for line in self.fhndl:
            if line.startswith('>'):
                res = FastaEntry(self.hdr, ''.join(self.seq))
                self.hdr = line.strip().split()[0][1:]
                self.seq = []
                break
            else:
                self.seq.append(line.strip())
        if res is None:
            res = FastaEntry(self.hdr, ''.join(self.seq))
            self.hdr = None
        return res

