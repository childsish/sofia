def findORFs(seq):
    stops = ('taa', 'tag', 'tga')
    res = []
    for i in xrange(len(seq)):
        if not seq[i:i + 3] == 'atg':
            continue
        for j in xrange(i, len(seq), 3):
            if seq[j:j + 3] in stops:
                res.append(seq[i:j + 3])
    return res
