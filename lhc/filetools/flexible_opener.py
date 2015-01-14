import bz2
import gzip


def open_flexibly(fname):
    if isinstance(fname, (file, bz2.BZ2File, gzip.GzipFile)):
        fhndl = fname
        fname = 'file'
    else:
        fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            open(fname)
    return fname, fhndl
