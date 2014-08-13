class VcfSet(object):
    def __init__(self, iterator):
        self.data = {(variant.chr, variant.pos): variant for variant in iterator}

    def __getitem__(self, key):
        return self.data[key]
