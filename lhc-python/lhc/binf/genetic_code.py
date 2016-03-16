import pkgutil


class RedundantCode(object):
    BASES = set('actgu')
    REDUNDANT_BASES = set('bdhkmnrsvwy')
    AMINO_ACIDS = set('ACDEFGHIKLMNPQRSTVWY*.BZX')
    CODE = {'a': 'a', 'c': 'c', 'g': 'g', 't': 't', 'u': 'u',
            'm': 'ac', 'r': 'ag', 'w': 'at',
            'k': 'gt', 'y': 'tc', 's': 'cg',
            'b': 'cgt', 'd': 'agt', 'h': 'act', 'v': 'acg', 'n': 'acgt'}
    REV =  {'a': 'a', 'c': 'c', 'g': 'g', 't': 't', 'u': 'u',
            'ac': 'm', 'ag': 'r', 'at': 'w',
            'gt': 'k', 'tc': 'y', 'cg': 's',
            'cgt': 'b', 'agt': 'd', 'act': 'h', 'acg': 'v', 'acgt': 'n'}

    def decode_codon(self, codon):
        codon = codon.lower()
        code = RedundantCode.CODE
        res = []
        for b1 in code[codon[0]]:
            for b2 in code[codon[1]]:
                for b3 in code[codon[2]]:
                    res.append(b1+b2+b3)
        return res

    def encode_codon(self, codons):
        rev = self.REV
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

    def valid_codon(self, codon):
        for c in codon:
            if c not in self.CODE:
                return False
        return True


class GeneticCode(object):

    NCODONS = 64
    REDUNDANT_CODE = RedundantCode()
    BASE2IDX = {'a': 0, 'c': 1, 'g': 2, 't': 3, 'u': 3}
    IDX2BASE = 'acgt'
    
    AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY*")

    def __init__(self, na2aa):
        self.__aa2na = {}
        self.__init_aa2na(na2aa)

        self.__na2aa = None
        self.__init_na2aa(na2aa)
    
    def __contains__(self, key):
        if not isinstance(key, str):
            raise TypeError('Expected codon or amino acid. Got {}: {}'.format(type(key), key))
        
        if key.upper() in GeneticCode.REDUNDANT_CODE.AMINO_ACIDS:
            return True
        return GeneticCode.REDUNDANT_CODE.valid_codon(key)
    
    def __getitem__(self, key):
        if isinstance(key, list):
            key = ''.join(key)
        if not isinstance(key, str):
            raise TypeError('Expected codon or amino acid. Got {}: {}'.format(type(key), key))
        elif len(key) != 1 and len(key) != 3:
            raise TypeError('Expected codon or amino acid. Got {}: len: {}'.format(type(key), key, len(key)))
        
        if key.upper() in GeneticCode.REDUNDANT_CODE.AMINO_ACIDS:
            return self.__aa2na[key.upper()]
        decode_codon = GeneticCode.REDUNDANT_CODE.decode_codon  # SPEED_HACK
        res = set([self.__na2aa[self._codon2index(codon)]
                   for codon in decode_codon(key)])
        if len(res) > 1:
            # raise ValueError('Codon "%s" does not match a specific codon family: %s'%\
            # (key, str(list(res))))
            res = ['X']
        return list(res)[0]

    def get_codons(self, aa):
        if aa not in GeneticCode.REDUNDANT_CODE.AMINO_ACIDS:
            aa = self[aa]
        return self.__aa2na[aa]

    def get_amino_acid(self, codon):
        return self.__na2aa[self._codon2index(codon)]
    
    def translate(self, na):
        return ''.join([self[na[i * 3:(i * 3) + 3]] for i in xrange(len(na) / 3)])
    
    def __init_aa2na(self, na2aa):
        setdefault = self.__aa2na.setdefault  # SPEED_HACK
        for key, val in na2aa.iteritems():
            setdefault(val, []).append(key)

    def __init_na2aa(self, na2aa):
        self.__na2aa = GeneticCode.NCODONS * [None]
        for key, val in na2aa.iteritems():
            self.__na2aa[self._codon2index(key)] = val

    def _codon2index(self, codon):
        codon = codon.lower()
        return 16 * self.BASE2IDX[codon[0]] +\
            4 * self.BASE2IDX[codon[1]] +\
            self.BASE2IDX[codon[2]]
        
    def _index2codon(self, index):
        codon = [self.IDX2BASE[index/16],
                 self.IDX2BASE[(index % 16)/4],
                 self.IDX2BASE[index % 4]]
        return "".join(codon)


class GeneticCodes:
    def __init__(self, fname=None):
        if fname is None:
            data = pkgutil.get_data('lhc', 'data/gc.prt')
        else:
            infile = open(fname)
            data = infile.read()
            infile.close()
        self.codes = {}
        self.name2id = {}
        self._parse_file(data)

    def __getitem__(self, key):
        if isinstance(key, basestring):
            key = self.name2id[key]
        return self.codes[key]

    def get_code(self, id):
        return self[id]
    
    def translate(self, seq, id):
        return self[id].translate(seq)
    
    def get_valid_names(self):
        return self.name2id.keys()
    
    def _parse_file(self, data):
        lines = iter(data.split('\n'))
        line = lines.next()
        names = []
        while True:
            if line[2:6] == 'name':
                names.append(line[line.find('"') + 1: line.rfind('"')])
            elif line[2:4] == 'id':
                id_ = int(line[5:line.find(',')].strip())
                na2aa = self._parse_code(lines)
                self.codes[id_] = GeneticCode(na2aa)
                for name in names:
                    self.name2id[name] = id_
                names = []
            try:
                line = lines.next()
            except StopIteration:
                break

    def _parse_code(self, lines):
        na2aa = {}#'NNN': 'X'}
        aa_line = lines.next()
        lines.next()
        _1 = lines.next()
        _2 = lines.next()
        _3 = lines.next()
        i = 12
        while aa_line[i] != '"':
            codon = (_1[i] + _2[i] + _3[i]).lower()
            na2aa[codon] = aa_line[i]
            i += 1
        return na2aa
