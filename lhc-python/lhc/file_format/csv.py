import os

from collections import namedtuple
from itertools import izip
from lhc.indices.index import Index

class CsvIterator(object):
    def __init__(self, fname, output=None, column_map=None, delimiter='\t', skip=1, line_comment='#'):
        self.fname = fname
        output = 'Entry' if output is None else output
        self.entry_tuple = namedtuple(output, [mapping['name'] for mapping in column_map])
        column_map = self._getColumnMap(fname) if column_map is None else column_map
        self.column_map = self._convertColumnMap(column_map)
        self.delimiter = delimiter
        self.skip = skip
        self.line_comment = line_comment
    
    def __iter__(self):
        fhndl = open(self.fname)
        entry_tuple = self.entry_tuple
        delimiter = self.delimiter
        column_map = self.column_map
        line_comment = self.line_comment
        skipped = 0
        for line in fhndl:
            if line.startswith(line_comment):
                continue
            skipped += 1
            if skipped >= self.skip:
                break
        for line in fhndl:
            # Assume all comments occur in the header.
            #if line.startswith(line_comment):
            #    continue
            parts = line.strip().split(delimiter)
            yield entry_tuple(*[eval(transform, {name: parts[index]}) for index, name, transform in column_map])
        fhndl.close()
    
    def _guessColumnMap(self, fname):
        fhndl = open(fname)
        skipped = 0
        for line in fhndl:
            if line.startswith(self.line_comment):
                continue
            elif skipped >= self.skip:
                parts = line.split(self.delimiter)
                fhndl.close()
                return [{'index': i, 'name': 'V%s'%i, 'transform': 'str(V%s)'%i} for i in xrange(len(parts))]
            skipped += 1
        fhndl.close()
        raise ValueError('Unable to parse %s'%fname)
    
    def _convertColumnMap(self, column_map):
        for mapping in column_map:
            if not 'transform' in mapping:
                mapping['transform'] = 'str(%s)'%mapping['name']
        return [(
                mapping['index'],
                mapping['name'],
                compile(mapping['transform'], '<string>', 'eval') if 'transform' in mapping else str
            ) for mapping in column_map]

class CsvSet(object):
    
    INDEX_TYPES = {}
    
    def __init__(self, iterator, indices):
        self.data = list(iter(iterator))
        self.indices = [(index_definition['required_attributes'], self._getIndex(index_definition, self.data)) for index_definition in indices]
    
    def __getitem__(self, key):
        for attributes, index in self.indices:
            match = index
            for attr in attributes:
                if not hasattr(key, attr):
                    match = None
                    break
            if match is None:
                raise KeyError('Can not find matching index for %s'%type(key))
        return self.data[match[key]]
    
    def _getIndex(self, index_definition, data):
        indices = []
        for mapping in index_definition['column_map']:
            indices.append(self.INDEX_TYPES[mapping['index']])
        index = Index(indices)
        for i, entry in enumerate(data):
            key = tuple(getattr(entry, mapping['name']) for mapping in index_definition['column_map'])
            index[key] = i
        return index
    
    @classmethod
    def registerIndexType(cls, index_type):
        cls.INDEX_TYPES[index_type.__name__] = index_type

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
    it = iterDir if os.path.isdir(fname) else iterFile
    return it(fname, column_builder, field_builder, skip)

def iterDir(dname, column_builder, field_builder, skip):
    for fname in os.listdir(dname):
        for row in iterFile(os.path.join(dname, fname), column_builder,
                field_builder, skip):
            yield row

def iterFile(fname, column_builder, field_builder, skip):
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
