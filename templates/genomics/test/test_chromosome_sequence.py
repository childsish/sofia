import unittest

from templates.genomics.steps.chromosome_sequence import GetHomopolymer
from lhc.io.vcf.iterator import Variant
from lhc.io.fasta.set_ import FastaSet


class TestChromosomeSequence(unittest.TestCase):
    def test_get_homopolymer(self):
        step = GetHomopolymer()

        chromosome_sequence_set = FastaSet([('1', 20 * 'a' + 80 * 'b')])
        v1 = Variant('1', 0, None, 'b', 'a')
        v2 = Variant('1', 0, None, 'b', 'ba')
        v3 = Variant('1', 0, None, 'ba', 'b')

        self.assertEquals(20 * 'a', step.calculate(v1, chromosome_sequence_set))
        self.assertEquals(19 * 'a', step.calculate(v2, chromosome_sequence_set))
        self.assertEquals(19 * 'a', step.calculate(v3, chromosome_sequence_set))


if __name__ == '__main__':
    unittest.main()
