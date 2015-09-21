__author__ = 'Liam Childs'

import unittest

from lhc.binf.sequence_generator import SequenceGenerator


class TestSequenceGenerator(unittest.TestCase):
    def test_generate(self):
        generator = SequenceGenerator()

        seq = generator.generate(10)

        self.assertEquals(10, len(seq))
        self.assertEquals(0, len(set(seq) - set('ACGT')))

    def test_generator_protein(self):
        generator = SequenceGenerator(SequenceGenerator.AMINO_ACIDS)

        seq = generator.generate(10)

        self.assertEquals(10, len(seq))
        self.assertNotEquals(0, len(set(seq) - set('ACGT')))
        self.assertEquals(0, len(set(seq) - set('ACDEFGHIKLMNPQRSTVWY')))

    def test_custom(self):
        generator = SequenceGenerator([('A', 0), ('C', 1), ('G', 0), ('T', 0)])

        seq = generator.generate(10)

        self.assertEquals('CCCCCCCCCC', seq)


if __name__ == '__main__':
    unittest.main()
