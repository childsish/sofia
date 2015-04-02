import json

from collections import OrderedDict, Sequence, Mapping


class JsonDict(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(JsonDict, self).__init__(*args, **kwargs)
        self.__root = self
    
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return super(JsonDict, self).__getattribute__(key)
    
    def __getitem__(self, key):
        v = super(JsonDict, self).__getitem__(key)
        if isinstance(v, basestring):
            v = v.format(**self.__root)
        return v
    
    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        if isinstance(value, Mapping) and not isinstance(value, JsonDict):
            value = JsonDict(value)
        elif isinstance(value, basestring):
            pass
        elif isinstance(value, Sequence) and not isinstance(value, JsonList):
            value = JsonList(value)
        super(JsonDict, self).__setitem__(key, value, dict_setitem)
    
    def set_as_root(self, root=None):
        if root is None:
            root = self
        self.__root = root
        for k, v in self.iteritems():
            if hasattr(v, 'set_as_root'):
                v.set_as_root(root)


class JsonList(list):

    ROOT_NAME = 'root'
    
    def __init__(self, *args, **kwargs):
        super(JsonList, self).__init__(*args, **kwargs)
        self.__root = {JsonList.ROOT_NAME: self}
    
    def __getitem__(self, key):
        v = super(JsonList, self).__getitem__(key)
        if isinstance(v, basestring):
            v = v.format(**self.__root)
        return v
    
    def __setitem__(self, key, value):
        if isinstance(value, Mapping) and not isinstance(value, JsonDict):
            value = JsonDict(value)
        elif isinstance(value, Sequence) and not isinstance(value, JsonList):
            value = JsonList(value)
        super(JsonList, self).__setitem__(key, value)
    
    def set_as_root(self, root=None):
        if root is None:
            root = {JsonList.ROOT_NAME: self}
        self.__root = root
        for v in self:
            if hasattr(v, 'set_as_root'):
                v.set_as_root(root)


def load(infile):
    infile.seek(0)
    data = json.load(infile, object_pairs_hook=JsonDict)
    data.set_as_root()
    return data


def loads(string):
    data = json.loads(string, object_pairs_hook=JsonDict)
    data.set_as_root()
    return data
