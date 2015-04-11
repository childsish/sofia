from resource import Target


class TableIterator(object):
    def __init__(self, fname, out_col):
        self.fhndl = open(fname)
        self.out_col = out_col
        self.line_no = 0

    def __iter__(self):
        return self

    def next(self):
        line = self.fhndl.readline()
        if line == '':
            raise StopIteration()
        parts = line.rstrip('\r\n').split('\t')
        return [parts[col] for col in self.out_col] + [tuple(parts)]


class TxtIterator(Target):

    EXT = {'.txt'}
    FORMAT = 'custom_table'

    def init(self, out_col):
        self.parser = TableIterator(self.get_filename(),
                                    [int(col) - 1 for col in out_col.split(',')])
