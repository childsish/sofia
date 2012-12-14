JOIN = 0
SPLIT = 1
IGNORE = 2

class TokeniserError(Exception):
    pass

class GenBankTokeniser:
    def tokenise(self, line):
        res = []
        fr = 0
        c_typ = self.__getTokenType(line[0])
        for to in xrange(len(line)-1):
            n_typ = self.__getTokenType(line[to+1])
            
            if c_typ[0] == JOIN and n_typ[1] != c_typ[1]:
                res.append(line[fr:to+1])
                fr = to+1
            elif c_typ[0] == SPLIT:
                res.append(line[fr:to+1])
                fr = to+1
            elif c_typ[0] == IGNORE:
                fr = to+1
            
            c_typ = n_typ
        res.append(line[fr:])
        return res
    
    def __getTokenType(self, char):
        """ Returns a 2-tuple (behaviour, type).
         behaviours:
          0 - join
          1 - split
          2 - ignore
        """
        if char in '()':
            return (SPLIT,0)
        elif char == ',':
            return (SPLIT,1)
        elif char in '<>':
            return (IGNORE,2)
        elif char == '.':
            return (JOIN,3)
        elif char.isdigit():
            return (JOIN,4)
        elif char.isalpha():
            return (JOIN,5)
        elif char == '^':
            return (JOIN,6)
        elif char.isspace():
            return (IGNORE,7)
        else:
            raise TokeniserError('TokeniserException: "%s" can not be tokenised'%char)

def tokenise(line):
    tokeniser = GenBankTokeniser()
    return tokeniser.tokenise(line)

def main():
    import random
    bases = 'actg'
    
    x1 = [0, 10]
    y1 = [5, 15]
    
    x2 = [10, 0]
    y2 = [15, 5]
    
    seq = ''.join([random.sample(bases, 1)[0] for i in xrange(20)])
    join1 = Join([Range(x1[i], y1[i]) for i in xrange(len(x1))])
    join2 = Join([Range(x2[i], y2[i]) for i in xrange(len(x1))])
    
    print seq
    print join1.getSubSeq(seq)
    print join2.getSubSeq(seq)

if __name__ == '__main__':
    import sys
    sys.exit(main())
