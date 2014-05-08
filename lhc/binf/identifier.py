import re

class Chromosome(object):
    
    CHR_REGX = re.compile('\d+$|X$|Y$|M$|C$')
    
    def __init__(self, name):
        self.name = name
        match = self.CHR_REGX.search(name)
        if match is None:
            raise ValueError('Unknown chromosome name: %s'%name)
        self.suffix = match.group(0)
        self.suffix = int(self.suffix) if self.suffix.isdigit() else self.suffix
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.suffix == other.suffix
    
    def __lt__(self, other):
        return self.suffix < other.suffix
