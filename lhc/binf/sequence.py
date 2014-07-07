import string

#from ushuffle import shuffle

_REVCMP = string.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN', 'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')

#def kshuffle(seq, k=2):
#    return shuffle(seq, len(seq), k)

def revcmp(seq):
    return seq.translate(_REVCMP)[::-1]
