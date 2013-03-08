from feature import Feature

class SequenceLength(Feature):
    def __init__(self):
        super(SequenceLength, self).__init__()

    def calculate(self, seq, dep_res):
        return {'len': len(seq)}

class OpenReadingFrames(Feature):
    pass
