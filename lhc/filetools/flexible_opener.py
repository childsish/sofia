import bz2
import gzip

from Bio import bgzf


def open_flexibly(fname):
    if isinstance(fname, (file, bz2.BZ2File, gzip.GzipFile, bgzf.BgzfReader)):
        fhndl = fname
        fname = 'file'
    else:
        fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            bgzf.open(fname) if fname.endswith('.bgz') else\
            open(fname)
    return fname, fhndl
