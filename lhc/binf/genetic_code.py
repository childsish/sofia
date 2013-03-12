#!/usr/bin/python

class RedundantCode:
    BASES = set("actgu")
    REDUNDANT_BASES = set("bdhkmnrsvwy")
    AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY*.BZX")
    CODE = {'a': 'a', 'c': 'c', 'g': 'g', 't': 't', 'u': 'u',
        'm': 'ac', 'r': 'ag', 'w': 'at',
        'k': 'gt', 'y': 'tc', 's': 'cg',
        'b': 'cgt', 'd': 'agt', 'h': 'act', 'v': 'acg', 'n': 'acgt'}
    REV  = {'a': 'a', 'c': 'c', 'g': 'g', 't': 't', 'u': 'u',
        'ac': 'm', 'ag': 'r', 'at': 'w',
        'gt': 'k', 'tc': 'y', 'cg': 's',
        'cgt': 'b', 'agt': 'd', 'act': 'h', 'acg': 'v', 'acgt': 'n'}
    
    def __init__(self):
        pass

    def decodeCodon(self, codon):
        codon = codon.lower()
        code = RedundantCode.CODE
        res = []
        for b1 in code[codon[0]]:
            for b2 in code[codon[1]]:
                for b3 in code[codon[2]]:
                    res.append(b1+b2+b3)
        return res

    def encodeCodon(self, codons):
        rev = RedundantCode.REV
        b1 = set()
        b2 = set()
        b3 = set()
        for codon in codons:
            b1.add(codon[0])
            b2.add(codon[1])
            b3.add(codon[2])
        
        return rev[''.join(sorted(list(b1)))] +\
               rev[''.join(sorted(list(b2)))] +\
               rev[''.join(sorted(list(b3)))]
    
    def validCodon(self, codon):
        for c in codon:
            if not c in RedundantCode.CODE:
                return False
        return True
    
class GeneticCode:

    NCODONS = 64
    REDUNDANT_CODE = RedundantCode()
    BASE2IDX = {'a': 0, 'c': 1, 'g': 2, 't': 3, 'u': 3}
    IDX2BASE = 'acgt'
    
    AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")

    def __init__(self, na2aa):
        self.__aa2na = {}
        self.__init_aa2na(na2aa)

        self.__na2aa = None
        self.__init_na2aa(na2aa)
    
    def __contains__(self, key):
        if not isinstance(key, str):
            raise TypeError('Expected codon or amino acid. Got ' + str(type(key)) + ': ' + str(key))
        
        if key.upper() in GeneticCode.REDUNDANT_CODE.AMINO_ACIDS:
            return True
        return GeneticCode.REDUNDANT_CODE.validCodon(key)
    
    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('Expected codon or amino acid. Got ' + str(type(key)) + ': ' + str(key))
        elif len(key) != 1 and len(key) != 3:
            raise TypeError('Expected codon or amino acid. Got ' + str(type(key)) + ': ' + str(key) + ' len:' + str(len(key)))
        
        if key.upper() in GeneticCode.REDUNDANT_CODE.AMINO_ACIDS:
            return self.__aa2na[key.upper()]
        decodeCodon = GeneticCode.REDUNDANT_CODE.decodeCodon #SPEED_HACK
        res = set([self.__na2aa[self.__codon2index(codon)]
                   for codon in decodeCodon(key)])
        if len(res) > 1:
            #raise ValueError('Codon "%s" does not match a specific codon family: %s'%\
            # (key, str(list(res))))
            res = ['X']
        return list(res)[0]

    def getCodons(self, aa):
        if not aa in GeneticCode.REDUNDANT_CODE.AMINO_ACIDS:
            aa = self[aa]
        return self.__aa2na[aa]

    def getAminoAcid(self, codon):
        return self.__na2aa[self.__codon2index(codon)]
    
    def translate(self, na):
        aa = (len(na) / 3) * [None]
        for i in xrange(len(aa)):
            aa[i] = self[na[i*3:(i*3)+3]]
        return ''.join(aa)

    def __init_aa2na(self, na2aa):
        setdefault = self.__aa2na.setdefault #SPEED_HACK
        for key, val in na2aa.iteritems():
            setdefault(val, []).append(key)

    def __init_na2aa(self, na2aa):
        self.__na2aa = GeneticCode.NCODONS * [None]
        for key, val in na2aa.iteritems():
            self.__na2aa[self.__codon2index(key)] = val

    def __codon2index(self, codon):
        codon = codon.lower()
        return 16 * GeneticCode.BASE2IDX[codon[0]] +\
            4 * GeneticCode.BASE2IDX[codon[1]] +\
                GeneticCode.BASE2IDX[codon[2]]
        
    def __index2codon(self, index):
        codon = [GeneticCode.IDX2BASE[index/16],
             GeneticCode.IDX2BASE[(index%16)/4],
             GeneticCode.IDX2BASE[index%4]]
        return "".join(codon)

class GeneticCodes:
    def __init__(self, filename):
        self.__codes = {}
        self.__name2id = {}
        self.__parseFile(filename)

    def __getitem__(self, key):
        if isinstance(key, basestring):
            key = self.__name2id[key]
        return self.__codes[key]

    def getCode(self, id):
        return self[id]
    
    def translate(self, seq, id):
        return self[id].translate(seq)
    
    def getValidNames(self):
        return self.__name2id.keys()
    
    def __parseFile(self, filename):
        infile = file(filename)
        line = infile.readline()
        names = []
        while line != '':
            if line[2:6] == 'name':
                names.append(line[line.find('"') + 1: line.rfind('"')])
            elif line[2:4] == 'id':
                id_ = int(line[5:line.find(',')].strip())
                na2aa = self.__parseCode(infile)
                self.__codes[id_] = GeneticCode(na2aa)
                for name in names:
                    self.__name2id[name] = id_
                names = []
            line = infile.readline()
        infile.close()

    def __parseCode(self, infile):
        na2aa = {}#'NNN': 'X'}
        aa_line = infile.readline()
        infile.readline()
        _1 = infile.readline()
        _2 = infile.readline()
        _3 = infile.readline()
        i = 12
        while aa_line[i] != '"':
            codon = (_1[i] + _2[i] + _3[i]).lower()
            na2aa[codon] = aa_line[i]
            i += 1
        return na2aa
