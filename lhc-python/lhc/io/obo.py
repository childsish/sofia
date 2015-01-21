class Term(dict):
    def __init__(self):
        self.__dict__ = self
    
def iterObo(fname, unq_keys=set(('id', 'name', 'namespace', 'def'))):
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
            k, v = [part.strip() for part in line.split(':', 1)]
            if k in unq_keys:
                term[k] = v
            else:
                term.setdefault(k, []).append(v)
    if term is not None:
        yield term
    infile.close()
