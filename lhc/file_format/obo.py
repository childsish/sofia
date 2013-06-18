class Term(dict):
    def __init__(self):
        self.__dict__ = self

def iterObo(fname):
    infile = open(fname)
    line = infile.next()
    while line.strip() != '[Term]':
        line = infile.next()
    term = Term()
    for line in infile:
        line = line.strip()
        if line == '':
            continue
        elif line[0] == '[':
            if term is not None:
                yield term
            
            if line == '[Term]':
                term = Term()
            else:
                term = None
        elif term is not None:
            k, v = line.split(':', 1)
            term[k.strip()] = v.strip()
    if term is not None:
        yield term
    infile.close()
