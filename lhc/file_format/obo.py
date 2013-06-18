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
        if line.strip() == '[Term]':
            yield term
            term = Term()
        else:
            k, v = line.strip().split(':', 1)
            term[k.strip()] = v.strip()
    yield term
    infile.close()
