__author__ = 'Liam Childs'


class GbkSequenceSet(object):
    def __init__(self, fileobj):
        fileobj = iter(fileobj)
        for line in fileobj:
            if line.startswith('ORIGIN'):
                break
        seq = []
        for line in fileobj:
            seq.extend(line.split()[1:])
        self.seq = ''.join(seq)

    def fetch(self, chr, start, stop):
        return self.seq[start:stop]
