class OmimSet(object):
    def __init__(self, iterator):
        self.data = {entry['NO']: entry for entry in iterator}

    def __getitem__(self, key):
        return self.data[key]

