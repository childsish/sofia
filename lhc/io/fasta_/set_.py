class FastaSet(object):
    def __init__(self, iterator):
        self.data = {k.split()[0]: v for k, v in iterator}

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.data[key]
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.data[key.chr][key.pos]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.data[key.chr][key.start:key.stop]
        raise NotImplementedError('Fasta set random access not implemented for {}'.format(type(key)))

    def fetch(self, chr, start, stop):
        return self.data[chr][start:stop]
