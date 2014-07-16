class FastaSet(object):
    def __init__(self, iterator):
        self.data = dict(iterator)
        self.prv_key = None
        self.prv_value = None

    def __getitem__(self, key):
        if self.prv_key == key:
            return self.prv_value
        else:
            self.prv_key = key
        
        if isinstance(key, basestring):
            self.prv_value = self.data[key]
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            self.prv_value =  self.data[key.chr][key.pos]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            self.prv_value =  self.data[key.chr][key.start:key.stop]
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return self.prv_value
