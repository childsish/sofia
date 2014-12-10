import string

_REVCMP = string.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN', 'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')

def revcmp(seq):
    return seq.translate(_REVCMP)[::-1]
