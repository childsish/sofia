import os
import pysam

from iterator import VcfIterator

class IndexedVcfFile(object):
    def __init__(self, fname, id_map=None):
        """ Initialise an indexed vcf file.
        
        :param fname: the name of the indexed vcf file.
            Must end in .vcf or .vcf.gz
        :param style: the style used to name the chromosome. Choice of ensemble
            and ucsc
        """
        self.fname = os.path.abspath(fname)
        iname = '%s.tbi'%self.fname
        if not os.path.exists(iname):
            raise ValueError('File missing interval index. Try: tabix -p vcf <FILENAME>.')
        self.index = pysam.Tabixfile(self.fname)
        self.iterator = VcfIterator(self.fname)
        self.id_map = id_map
    
    def __getitem__(self, key):
        if not hasattr(key, 'chr'):
            raise NotImplementedError('Random access not implemented for %s'%\
                type(key))
        #TODO: assumes a single mapping
        chr = key.chr if self.id_map is None else list(self.id_map[key.chr])[0]
        start = key.start if hasattr(key, 'start') else\
                key.pos if hasattr(key, 'pos') else\
                None
        if start is None:
            raise NotImplementedError('Random access not implemented for %s'%\
                type(key))
        stop = key.stop if hasattr(key, 'stop') else\
               start + len(key.ref) if hasattr(key, 'ref') else\
               start + 1
        lines = self.index.fetch(chr, start, stop)
        return [self.iterator._parseLine(line) for line in lines]
    
    def getVariantsAtPosition(self, chr, pos):
        lines = self.index.fetch(chr, pos, pos + 1)
        return [self.iterator._parseLine(line) for line in lines]
    
    def getVariantsInInterval(self, chr, start, stop):
        line = self.index.fetch(chr, start, stop)
        return [self.iterator._parseLine(line) for line in lines]
