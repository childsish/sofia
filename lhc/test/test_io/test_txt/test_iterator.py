import os
import tempfile
import unittest

from lhc.binf.genomic_coordinate import GenomicInterval as Interval
from lhc.io.txt_ import Iterator, Entity, Column


class TestITerator(unittest.TestCase):
    def setUp(self):
        self.data = [('1', '10', '20', 'a'),
                     ('1', '30', '60', 'b'),
                     ('1', '100', '110', 'c'),
                     ('2', '15', '30', 'd'),
                     ('2', '40', '50', 'e'),
                     ('3', '10', '110', 'f')]
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '\n'.join('\t'.join(row) for row in self.data))
        os.close(fhndl)

    def test_iterator_plain(self):
        it = Iterator(open(self.fname))

        self.assertEquals(self.data[0], tuple(it.next()))
        self.assertEquals(self.data[1], tuple(it.next()))
        self.assertEquals(self.data[2], tuple(it.next()))
        self.assertEquals(self.data[3], tuple(it.next()))
        self.assertEquals(self.data[4], tuple(it.next()))
        self.assertEquals(self.data[5], tuple(it.next()))
        self.assertRaises(StopIteration, it.next)

    def test_iterator_builder(self):
        entity_factory = Entity(Interval, [Column(str, 0, 'chr'), Column(int, 1, 'start'), Column(int, 2, 'stop')])
        it = Iterator(open(self.fname), entry_factory=entity_factory)

        self.assertEquals(Interval('1', 10, 20), it.next())
        self.assertEquals(Interval('1', 30, 60), it.next())
        self.assertEquals(Interval('1', 100, 110), it.next())
        self.assertEquals(Interval('2', 15, 30), it.next())
        self.assertEquals(Interval('2', 40, 50), it.next())
        self.assertEquals(Interval('3', 10, 110), it.next())
        self.assertRaises(StopIteration, it.next)


if __name__ == '__main__':
    unittest.main()
