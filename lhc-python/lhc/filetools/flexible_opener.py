import gzip

from StringIO import StringIO


def open_flexibly(fname, mode='r'):
    if isinstance(fname, (file, gzip.GzipFile)):
        fhndl = fname
        fname = 'file'
    elif isinstance(fname, StringIO):
        fhndl = fname
        fname = 'stringio'
    else:
        fhndl = gzip.open(fname, mode) if fname.endswith('.gz') else\
            open(fname, mode)
    return fname, fhndl
