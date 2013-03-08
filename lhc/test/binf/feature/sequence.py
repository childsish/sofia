from unittest import TestCase, main

from lhc.binf.feature.sequence import SequenceLength

class TestSequenceLength(TestCase):
    def test_generate(self):
        seq = 'cttatagcgatg'
        gen = SequenceLength()

        res = gen.generate(gen.transform(seq))
        
        self.assertEquals(res, {'len': 12})

if __name__ == '__main__':
    import sys
    sys.exit(main())
