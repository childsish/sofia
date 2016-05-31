import os


def load_resource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: {}'.format(os.path.basename(fname)))


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]
