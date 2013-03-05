#!/usr/bin/python

import os
import stat
import cPickle

from header import getSequenceId

class FastaIndex(object):
    def __init__(self, fname):
        self.fname = fname
        self.source = None
        self.wrap = None
        self.newlines = None
        self.seq_idxs = None
        if os.path.exists(fname):
            self._loadIndex(fname)
    
    def __del__(self):
        if not os.path.exists(self.fname):
            self._dumpIndex(self.fname)
    
    def _loadIndex(self, fname):
        infile = open(fname, 'rb')
        mtime = cPickle.load(infile)
        self.source = cPickle.load(infile)
        if mtime != os.stat(self.source)[stat.ST_MTIME]:
            raise OSError('Index is out-of-synch with source')
        self.wrap = cPickle.load(infile)
        self.newlines = cPickle.load(infile)
        self.seq_idxs = cPickle.load(infile)
        infile.close()

    def _dumpIndex(self, fname):
        mtime = os.stat(self.source)[stat.ST_MTIME]
        outfile = file(fname, 'wb')
        cPickle.dump(mtime, outfile, cPickle.HIGHEST_PROTOCOL)
        cPickle.dump(self.source, outfile, cPickle.HIGHEST_PROTOCOL)
        cPickle.dump(self.wrap, outfile, cPickle.HIGHEST_PROTOCOL)
        cPickle.dump(self.newlines, outfile, cPickle.HIGHEST_PROTOCOL)
        cPickle.dump(self.seq_idxs, outfile, cPickle.HIGHEST_PROTOCOL)
        outfile.close()

class IndexedFastaSequence(object):
    """ An indexed sequence into a fasta file. Retrieving a sequence involves
    opening a file finding the start and stop indices, returning the
    stripped and joined lines between them and closing the file.
    Currently unsure whether this will work on different platforms.
    """
    
    CHUNK = 2048
    
    def __init__(self, idx, idx_hdr, idx_fr, idx_to, pos_fr=0, pos_to=None):
        """ Intialises the entry. """
        self.idx = idx
        self.idx_hdr = idx_hdr
        self.idx_fr = idx_fr
        self.idx_to = idx_to
        self.pos_fr = pos_fr
        self.pos_to = self.convertIndexToPosition(idx_to)\
            if pos_to is None else pos_to
    
    def __len__(self):
        return int(self.pos_to - self.pos_fr)
    
    def __str__(self):
        idx_fr = self.convertPositionToIndex(self.pos_fr)
        idx_to = self.convertPositionToIndex(self.pos_to)
        sz = idx_to - idx_fr
        infile = open(self.idx.source)
        infile.seek(idx_fr)
        seq = infile.read(sz)
        infile.close()
        return seq.replace(self.idx.newlines, '')
    
    def __getitem__(self, key):
        if isinstance(key, int):
            offset = self.convertPositionToIndex(key)
            if offset < self.pos_fr or offset >= self.pos_to:
                raise IndexError('string index out of range')
            seq = IndexedFastaSequence(self.idx.source, self.idx_hdr, self.idx_fr,
                self.idx_to, self.idx.wrap, self.idx.newlines, key, key + 1)
            return str(seq)
        elif isinstance(key, slice):
            fr = self.pos_fr + key.start
            to = self.pos_fr + key.stop
            
            if fr > self.pos_to:
                fr = self.pos_to
            if to > self.pos_to:
                to = self.pos_to
            
            seq = IndexedFastaSequence(self.idx.source, self.idx_hdr, self.idx_fr,
                self.idx_to, self.idx.wrap, self.idx.newlines, fr, to)
            return seq
        raise KeyError('Invalid key type: %s'%type(key))
    
    def __iter__(self):
        chunk = IndexedFastaSequence.CHUNK
        for i in xrange(0, self.pos_to - self.pos_fr, chunk):
            sub = self[i:i + chunk]
            for base in str(sub):
                yield base
    
    def convertIndexToPosition(self, idx):
        """ Calculate the position of the given index from the start of the
        sequence.
        """
        return (((idx + 1) - self.idx_fr) * self.idx.wrap) /\
            (self.idx.wrap + len(self.idx.newlines))
    
    def convertPositionToIndex(self, pos):
        """ Calculate the offset of the given position from the start of the
        sequence.
        """
        return pos + (pos / self.idx.wrap) * len(self.idx.newlines) + self.idx_fr
    
    def getHeader(self):
        infile = open(self.idx.source, 'rU')
        infile.seek(self.idx_hdr)
        hdr = getHeader(infile.readline())
        infile.close()
        return hdr

class FastaDictionary(object):
    def __init__(self, fname):
        self.fname = fname
        iterator = FastaIterator(fname)
        self.data = dict((getSequenceId(hdr), seq) for hdr, seq in iterator)
    
    def __getitem__(self, key):
        return self.data[key]

class FastaIndexedDictionary(object):
    def __init__(self, iname):
        self.iname = iname
    
    def __get__(self, key):
        idx = FastaIndex(self.iname)
        idx_hdr, idx_fr, idx_to = idx.seq_idxs[hdr]
        return IndexedFastaSequence(idx, idx_hdr, idx_fr, idx_to)

class FastaIterator(object):
    def __init__(self, fname):
        self.fname = fname
    
    def __iter__(self):
        infile = open(self.fname, 'rU')
        hdr = None
        seq = None
        for line in infile:
            if line[0] == '>':
                if hdr != None:
                    yield (hdr, ''.join(seq))
                hdr = line.strip()[1:]
                seq = []
            else:
                seq.append(line.strip())
        yield hdr, ''.join(seq)
        infile.close()

class FastaIndexedIterator(object):
    def __init__(self, iname):
        self.idx = FastaIndex(iname)
    
    def __iter__(self):
        idx = FastaIndex(iname)
        for hdr, rng in idx.seq_idxs.iteritems():
            idx_hdr, idx_fr, idx_to = rng
            seq = IndexedFastaSequence(idx, idx_hdr, idx_fr, idx_to)
            yield seq.getHeader(), seq

def writeFasta(ents, fname, width=0):
    outfile = open(fname, 'w')
    if width == 0:
        for ent in ents:
            outfile.write('>%s\n%s\n'%(ent))
    else:
        for hdr, seq in ents:
            outfile.write('>%s\n'%hdr)
            for i in xrange(0, len(seq), width):
                outfile.write(seq[i:i+width])
                outfile.write('\n')
    outfile.close()

def iterFasta(fname):
    iname = getIndexName(fname)
    if os.path.exists(iname):
        return FastaIndexedIterator(iname).__iter__()
    return FastaIterator(fname).__iter__()

def getIndexName(fname):
    if '.' in fname:
        iname = fname[:fname.rfind('.')] + '.idx'
    else:
        iname = fname + '.idx'
    return iname

def extractFasta(fname, hdr):
    iname = getIndexName(fname)
    if os.path.exists(iname):
        return FastaIndexedDictionary(iname)[hdr]
    return FastaDictioanry(fname)[hdr]

def getHeader(line):
    return line.strip().split()[0][1:]

def indexFasta(fname, iname=None):
    from collections import OrderedDict
    iname = getIndexName(fname) if iname is None else iname
    idx = FastaIndex(iname)
    
    # Determine the wrap size
    wrap = getWrap(fname)
    if wrap is None:
        raise ValueError('Could not find a valid sequence line in fasta file')
    infile = open(fname, 'rU')
    idxs = OrderedDict()
    lineno = 0
    hdr = None
    prv_wrap = None
    while True: # Equivalent of do-while loop.
        idx_to = infile.tell()
        line = infile.readline()
        if len(line) == 0: # Exit condition
            if hdr is not None:
                idxs[hdr] = (idx_hdr, idx_fr, infile.tell())
            break
        elif line[0] == '>':
            if hdr is not None:
                idxs[hdr] = (idx_hdr, idx_fr, idx_to)
            hdr = getHeader(line)
            idx_hdr = idx_to
            idx_fr = infile.tell()
            prv_wrap = None
        elif line[0] != '#' and prv_wrap != None and prv_wrap != wrap:
            raise ValueError('Line %d does not have %d characters'%\
                (lineno, wrap))
        else:
            prv_wrap = len(line.strip())
        lineno += 1
    idx.source = fname
    idx.wrap = wrap
    idx.newlines = infile.newlines
    idx.seq_idxs = idxs
    infile.close()
    return iname

def getWrap(fname):
    wrap = None
    infile = open(fname, 'rU')
    for line in infile:
        if line[0] not in '#>':
            wrap = len(line.strip())
            break
    infile.close()
    return wrap

def splitFasta(infname, npart, outdname=None):
    if outdname == None:
        import tempfile
        outdname = tempfile.mkdtemp()
    elif not os.path.exists(outdname):
        os.makedirs(outdname)
    
    infile = open(infname, 'rU')
    i = -1
    outs = []
    for line in infile:
        if line.startswith('>'):
            i = (i+1)%npart
            if i == len(outs):
                outfile = open(os.path.join(outdname, '%s.fasta'%(i)), 'w')
                outs.append(outfile)
        outs[i].write(line)
    infile.close()
    for outfile in outs:
        outfile.close()
    
    return (outdname, [outfile.name for outfile in outs])

def flattenFasta(infname):
    import shutil
    from tempfile import mkstemp
    
    outfile, outfname = mkstemp()
    os.close(outfile)
    writeFasta(iterFasta(infname), outfname)
    shutil.move(outfname, infname)

def main(argv = None):
    if argv[1] == 'index':
        indexFasta(argv[2])
    elif argv[1] == 'split':
        splitFasta(argv[2], int(argv[3]), '%s_%s'%(argv[2], argv[3]))
    elif argv[1] == 'flatten':
        flattenFasta(argv[2])
    elif argv[1] == 'extract':
        extract_sequence(argv[2], int(argv[3]), int(argv[4]))
    else:
        print 'Argument 1 must be either index or flatten'

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
