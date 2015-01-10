class Transformer(object):
    def transform(self, seq):
        raise NotImplementedError('You must override this function')

class Seq2Seq(Transformer):
    def transform(self, seq):
        return seq

class Seq2Str(Transformer):
    def transform(self, seq):
        pass

class Str2Gra(Transformer):
    def transform(self, seq):
        pass
