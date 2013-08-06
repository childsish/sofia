from collections import namedtuple

class ColumnBuilder(object):
    
    COLUMN = namedtuple('Column', ['name', 'idx', 'type'])
    
    def __init__(self):
        self.cols = []
        self.tuple = None
    
    def __call__(self, parts):
        return self.tuple._make(col.type(parts[col.idx]) for col in self.cols)
    
    def registerColumn(self, name, idx, typ=str):
        self.cols.append(ColumnBuilder.COLUMN(name, idx, typ))
        self.tuple = namedtuple('CsvRow', [col.name for col in self.cols])


class FieldBuilder(object):
    
    FIELD = namedtuple('Field', ['name', 'fn'])
    
    def __init__(self):
        self.fields = []
        self.tuple = None
    
    def __call__(self, columns):
        return self.tuple._make(field.fn(columns) for field in self.fields)
    
    def registerField(self, name, fn=None):
        fn = (lambda x:getattr(x, name)) if fn is None else fn
        self.fields.append(FieldBuilder.FIELD(name, fn))
        self.tuple = namedtuple('CsvRow', [field.name for field in self.fields])


def iterCsv(fname, column_builder=None, field_builder=None, skip=0):
    infile = open(fname)
    line = infile.next()
    while line.startswith('#'):
        line = infile.next()
    for i in xrange(skip):
        line = infile.next()
    filters = [f for f in (column_builder, field_builder) if f is not None]
    while line != '':
        res = line.strip().split('\t')
        for f in filters:
            res = f(res)
        yield res
        line = infile.next()
    infile.close()