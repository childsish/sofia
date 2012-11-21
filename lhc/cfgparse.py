import re

from datetime import datetime
from functools import partial

def parseBoolean(value):
    value = value.lower()
    if value not in ('true', 'false'):
        raise ValueError('This value is not a boolean.')
    return value == 'true'

def parseDictionary(value):
    if value[0] != '{' and value[-1] != '}':
        raise ValueError('This value is not a dictionary')
    parts = (part.split(':') for part in value[1:-1].split(','))
    return dict((p1.strip(), p2.strip()) for p1, p2 in parts)

class Configuration(dict):
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key):
        return getattr(self, key) if key in self else None

    def __getitem__(self,key):
        return dict.get(self, key, None)

    def copy(self):
        self.__dict__ = {}
        s = FastStorage(self)
        self.__dict__ = self
        return s

    def __repr__(self):
        return '<Configuration %s>' % dict.__repr__(self)

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, sdict):
        dict.__init__(self, sdict)
        self.__dict__ = self

    def update(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

class ConfigurationParser(object):
    
    KEY_REGX = re.compile('^[a-zA-Z_]\w*?$')
    VALUE_PARSERS = [parseBoolean,
        int,
        partial(int, base=8),
        partial(int, base=16),
        complex,
        lambda v: datetime.strptime(v, '%Y-%m-%d'), #partial(datetime.strptime, format='%Y-%m-%d'),
        lambda v: datetime.strptime(v, '%Y-%m-%d %H:%M:%S'), #partial(datetime.strptime, format='%Y-%m-%d %H:%M:%S'),
        parseDictionary,
        str
    ]

    def __init__(self):
        self.cfg = None
        self.stk = []
        self.value_parsers = self.VALUE_PARSERS[:]

    def loads(self, text):
        self.cfg = cfg = Configuration()
        for line in text.splitlines():
            if line[0] != '#':
                self.parseLine(line)
        self.cfg = None
        return cfg

    def parseLine(self, line):
        key, val = line.strip().split(': ', 1)
        if not self.isValidKey(key):
            raise ValueError('Invalid key: %s'%key)
        val = self.parseValue(val.strip())
        self.cfg[key] = val
        indent = len(line) - len(line.strip())

    def isValidKey(self, key):
        match = self.KEY_REGX.match(key)
        return match is not None

    def parseValue(self, val):
        for parser in self.value_parsers:
            try:
                val = parser(val)
            except ValueError:
                continue
            except TypeError, e:
                if isinstance(parser, partial):
                    continue
                raise e
            return val
        return val

    def raiseLevel(self, key, indent):
        lvl = Configuration()
        lvl.key = key
        lvl.indent = indent
        self.stk.append(lvl)

    def lowerLevel(self):
        self.stk.pop()

def load(file_name):
    with open(file_name) as infile:
        res = loadh(infile)
    return res

def loadh(file_handle):
    parser = ConfigurationParser()
    return loads(file_handle.read())

def loads(text):
    parser = ConfigurationParser()
    return parser.loads(text)
