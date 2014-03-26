import os

from modules.entitites import Sequence
from modules.genomic_coordinate import Point
from modules.indices.string_index import StringIndex
from modules.indices.point_index import PointIndex
from modules.resource import Resource

class Fasta(Resource):
    
    NAME = 'fasta'
    
    def __init__(self, fname, iname=None):
        super(Fasta, self).__init__(fname, iname)
        if iname is not None:
            self.stridx = StringIndex(os.path.join(iname, 'str.%s'%StringIndex.EXT))
            self.pntidx = PointIndex(os.path.join(iname, 'pnt.%s'%PointIndex.EXT))
    
    def __iter__(self):
        infile = open(self.fname)
        hdr = self.resource.next()[1:].split()[0]
        seq = []
        while True:
            line = self.resource.next()
            if line == '':
                break
            elif line[0] == '>':
                yield Sequence(hdr, ''.join(seq))
                hdr = line[1:].split()[0]
                seq = []
            seq.append(line.strip())
        infile.close()

    def __getitem__(self, key):
        infile = open(self.fname)
        if isinstance(key, basestring):
            file_pos = self.stridx[key]
            infile.seek(file_pos)
            infile.readline() # read the header
            seq = [line for line in infile if not line.startswith('>')]
            return ''.join(seq)
        
        if hasattr(key, 'pos'):
            file_pos, idxpos = self.pntidx[key]
            delta = key.pos - idxpos
            infile.seek(file_pos + delta)
            return infile.read(1)
        elif hasattr(key, 'start') and hasattr(self, 'stop'):
            fpos_fr, idxstart = self.pntidx[key.start]
            delta_fr = key.start - idxstart
            fpos_to, idxstop = self.pntidx[key.stop]
            delta_to = key.stop - idxstop
            infile.seek(fpos_fr + delta_fr)
            seq = infile.read(fpos_to - fpos_fr - delta_fr + delta_to)
            return ''.join(seq.split())
        msg = 'Can not get sequence from fasta using this key type: {type}'
        raise TypeError(msg.format(type=type(key)))
    
    def index(self, iname):
        os.mkdir(iname)
        self.pntidx = PointIndex(os.path.join(iname, 'pos.%s'%PointIndex.EXT))
        self.stridx = StringIndex(os.path.join(iname, 'str.%s'%StringIndex.EXT))
        infile = open(self.fname)
        hdr = infile.readline().strip().split()[0][1:]
        pos = 0
        while True:
            file_pos = infile.tell()
            line = infile.readline().strip()
            if line == '': #do-while
                break
            elif line.startswith('>'):
                self.stridx[hdr] = file_pos
                hdr = line.split()[0][1:]
                pos = 0
            self.pntidx[Point(hdr, pos)] = file_pos
            pos += len(line)
        infile.close()
