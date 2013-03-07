import re

class CodonUsageTable:
    
    REGX = re.compile(r'(?P<codon>[ACGU]{3})\s+(?P<frq>\d+\.\d+)\((\s+\d+)\)')
    
    def __init__(self, filename):
        self.__codons = {}
        
        infile = open(filename)
        for line in infile:
            matches = CodonUsageTable.REGX.findall(line)
            for match in matches:
                self.__codons[match[0].lower().replace('u', 't')] = float(match[2])
        infile.close()
    
    def __str__(self):
        res = ['%s\t%d'%(codon, value)
         for codon, value in sorted(self.__codons.iteritems())]
        return '\n'.join(res)
            
    
    def __getitem__(self, key):
        return self.__codons[key]

def main():
    import os
    outfile = open('tmp.cut', 'w')
    outfile.write('UUU  1.0(     1)  UCU  1.0(     1)  UAU  1.0(     1)  UGU  1.0(     1)\n'
     'UUC  1.0(     1)  UCC  1.0(     1)  UAC  1.0(     1)  UGC  1.0(     1)\n'
     'UUA  1.0(     1)  UCA  1.0(     1)  UAA  1.0(     1)  UGA  1.0(     1)\n'
     'UUG  1.0(     1)  UCG  1.0(     1)  UAG  1.0(     1)  UGG  1.0(     1)\n'
     'CUU  1.0(     1)  CCU  1.0(     1)  CAU  1.0(     1)  CGU  1.0(     1)\n'
     'CUC  1.0(     1)  CCC  1.0(     1)  CAC  1.0(     1)  CGC  1.0(     1)\n'
     'CUA  1.0(     1)  CCA  1.0(     1)  CAA  1.0(     1)  CGA  1.0(     1)\n'
     'CUG  1.0(     1)  CCG  1.0(     1)  CAG  1.0(     1)  CGG  1.0(     1)\n'
     'AUU  1.0(     1)  ACU  1.0(     1)  AAU  1.0(     1)  AGU  1.0(     1)\n'
     'AUC  1.0(     1)  ACC  1.0(     1)  AAC  1.0(     1)  AGC  1.0(     1)\n'
     'AUA  1.0(     1)  ACA  1.0(     1)  AAA  1.0(     1)  AGA  1.0(     1)\n'
     'AUG  1.0(     1)  ACG  1.0(     1)  AAG  1.0(     1)  AGG  1.0(     1)\n'
     'GUU  1.0(     1)  GCU  1.0(     1)  GAU  1.0(     1)  GGU  1.0(     1)\n'
     'GUC  1.0(     1)  GCC  1.0(     1)  GAC  1.0(     1)  GGC  1.0(     1)\n'
     'GUA  1.0(     1)  GCA  1.0(     1)  GAA  1.0(     1)  GGA  1.0(     1)\n'
     'GUG  1.0(     1)  GCG  1.0(     1)  GAG  1.0(     1)  GGG  1.0(     1)\n')
    outfile.close()
    
    table = CodonUsageTable('tmp.cut')
    print table['AAA']
    
    os.remove('tmp.cut')

if __name__ == '__main__':
    import sys
    sys.exit(main())
