import gzip

from Bio import bgzf
from StringIO import StringIO


def open_flexibly(fname, mode='r'):
    if isinstance(fname, (file, gzip.GzipFile, bgzf.BgzfReader)):
        fhndl = fname
        fname = 'file'
    elif isinstance(fname, StringIO):
        fhndl = fname
        fname = 'stringio'
    else:
        fhndl = gzip.open(fname, mode) if fname.endswith('.gz') else\
            bgzf.open(fname, mode) if fname.endswith('.bgz') else\
            open(fname, mode)
    return fname, fhndl
