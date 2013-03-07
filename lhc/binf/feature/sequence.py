from feature import Feature

class SequenceLength(Feature):
    def __init__(self):
        super(SequenceLength, self).__init__()

    def generate(self, seq):
        return len(seq)

    def calculate(self, seq):
        return len(seq)

