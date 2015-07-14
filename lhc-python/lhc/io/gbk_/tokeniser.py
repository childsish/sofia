class GenbankTokeniser(object):

    JOIN = 0
    SPLIT = 1
    IGNORE = 2

    def tokenise(self, line):
        res = []
        fr = 0
        c_typ = self._get_token_type(line[0])
        for to in xrange(len(line)-1):
            n_typ = self._get_token_type(line[to+1])
            
            if c_typ[0] == self.JOIN and n_typ[1] != c_typ[1]:
                res.append(line[fr:to+1])
                fr = to+1
            elif c_typ[0] == self.SPLIT:
                res.append(line[fr:to+1])
                fr = to+1
            elif c_typ[0] == self.IGNORE:
                fr = to+1
            
            c_typ = n_typ
        res.append(line[fr:])
        return res
    
    def _get_token_type(self, char):
        """ Returns a 2-tuple (behaviour, type).
         behaviours:
          0 - join
          1 - split
          2 - ignore
        """
        if char in '()':
            return self.SPLIT, 0
        elif char == ',':
            return self.SPLIT, 1
        elif char in '<>':
            return self.IGNORE, 2
        elif char == '.':
            return self.JOIN, 3
        elif char.isdigit():
            return self.JOIN, 4
        elif char.isalpha():
            return self.JOIN, 5
        elif char == '^':
            return self.JOIN, 6
        elif char.isspace():
            return self.IGNORE, 7
        else:
            raise ValueError('TokeniserException: "{}" can not be tokenised'.format(char))
