import cPickle
import unittest

from lhc.binf.genomic_coordinate import Interval
from lhc.binf.genomic_feature import GenomicFeature


class TestGenomicFeature(unittest.TestCase):
    def test_init_with_defaults(self):
        feature = GenomicFeature('l1', 'gene')
        self.assertEquals('l1', feature.name)
        self.assertEquals('gene', feature.type)
        self.assertEquals(None, feature.chr)
        self.assertEquals(None, feature.start)
        self.assertEquals(None, feature.stop)

    def test_init_with_interval(self):
        feature = GenomicFeature('l1', 'gene', Interval('1', 0, 1000))
        self.assertEquals('l1', feature.name)
        self.assertEquals('gene', feature.type)
        self.assertEquals('1', feature.chr)
        self.assertEquals(0, feature.start)
        self.assertEquals(1000, feature.stop)

    def test_length(self):
        l2a = Interval('1', 0, 1000)
        l3a = Interval('1', 0, 300)
        l3b = Interval('1', 700, 1000)

        feature = GenomicFeature('l2a', 'gene', l2a)
        self.assertEquals(1000, len(feature))

        feature.add_child(GenomicFeature('l3a', 'transcript', l3a))
        feature.add_child(GenomicFeature('l3b', 'transcript', l3b))
        self.assertEquals(600, len(feature))

    def test_getitem(self):
        l1 = Interval('1', 0, 1000)
        l2a = Interval('1', 0, 1000)
        l2b = Interval('1', 0, 1000)
        l3a = Interval('1', 0, 300)
        l3b = Interval('1', 700, 1000)
        l3c = Interval('1', 0, 300)
        l3d = Interval('1', 400, 600)
        l3e = Interval('1', 700, 1000)

        feature = GenomicFeature('l1', 'gene', l1)
        feature.add_child(GenomicFeature('l2a', 'transcript', l2a))
        feature.add_child(GenomicFeature('l2b', 'transcript', l2b))
        self.assertEquals(0, feature['l1'].start)
        self.assertEquals(0, feature['l2a'].start)
        self.assertEquals(0, feature['l2b'].start)

        feature['l2a'].add_child(GenomicFeature('l3a', 'CDS', l3a))
        feature['l2a'].add_child(GenomicFeature('l3b', 'CDS', l3b))
        feature['l2b'].add_child(GenomicFeature('l3c', 'CDS', l3c))
        feature['l2b'].add_child(GenomicFeature('l3d', 'CDS', l3d))
        feature['l2b'].add_child(GenomicFeature('l3e', 'CDS', l3e))
        self.assertEquals(300, feature['l3a'].stop)
        self.assertEquals(700, feature['l3b'].start)
        self.assertEquals(300, feature['l3c'].stop)
        self.assertEquals(400, feature['l3d'].start)
        self.assertEquals(700, feature['l3e'].start)

        self.assertIsNone(feature['a'])

    def test_get_abs_pos(self):
        self.skipTest('not implemented')
        l2b = Interval('1', 0, 1000)
        l3c = Interval('1', 0, 300)
        l3d = Interval('1', 400, 600)
        l3e = Interval('1', 700, 1000)
        l4a = Interval('1', 700, 750)
        l4b = Interval('1', 950, 1000)

        feature = GenomicFeature('l2b', 'transcript', l2b)
        feature.add_child(GenomicFeature('l3c', 'CDS', l3c))
        feature.add_child(GenomicFeature('l3d', 'CDS', l3d))
        feature.add_child(GenomicFeature('l3e', 'CDS', l3e))
        feature['l3e'].add_child(GenomicFeature('l4a', 'CDS', l4a))
        feature['l3e'].add_child(GenomicFeature('l4b', 'CDS', l4b))

        self.assertEquals(0, feature.get_abs_pos(0))
        self.assertEquals(299, feature.get_abs_pos(299))
        self.assertEquals(400, feature.get_abs_pos(300))
        self.assertEquals(599, feature.get_abs_pos(499))
        self.assertEquals(700, feature.get_abs_pos(500))
        self.assertEquals(749, feature.get_abs_pos(549))
        self.assertEquals(950, feature.get_abs_pos(550))
        self.assertRaises(IndexError, feature.get_abs_pos, -1)
        self.assertRaises(IndexError, feature.get_abs_pos, 800)

    def test_get_rel_pos(self):
        l2b = Interval('1', 0, 1000)
        l3c = Interval('1', 0, 300)
        l3d = Interval('1', 400, 600)
        l3e = Interval('1', 700, 1000)
        l4a = Interval('1', 700, 750)
        l4b = Interval('1', 950, 1000)

        feature = GenomicFeature('l2b', 'transcript', l2b)
        feature.add_child(GenomicFeature('l3c', 'CDS', l3c))
        feature.add_child(GenomicFeature('l3d', 'CDS', l3d))
        feature.add_child(GenomicFeature('l3e', 'CDS', l3e))
        feature['l3e'].add_child(GenomicFeature('l4a', 'CDS', l4a))
        feature['l3e'].add_child(GenomicFeature('l4b', 'CDS', l4b))

        self.assertEquals(0, feature.get_rel_pos(0))
        self.assertEquals(299, feature.get_rel_pos(299))
        self.assertEquals(300, feature.get_rel_pos(400))
        self.assertEquals(499, feature.get_rel_pos(599))
        self.assertEquals(500, feature.get_rel_pos(700))
        self.assertEquals(549, feature.get_rel_pos(749))
        self.assertEquals(550, feature.get_rel_pos(950))
        self.assertRaises(IndexError, feature.get_rel_pos, -1)
        self.assertRaises(IndexError, feature.get_rel_pos, 300)
        self.assertRaises(IndexError, feature.get_rel_pos, 750)

    def test_get_sub_seq(self):
        import random
        import string
        seq = ''.join(random.sample(string.letters, 1)[0] for i in xrange(100))

        l2b = Interval('1', 0, 100)
        l3c = Interval('1', 0, 30)
        l3d = Interval('1', 40, 60)
        l4a = Interval('1', 0, 5)
        l4b = Interval('1', 25, 30)

        feature = GenomicFeature('l2b', 'transcript', l2b)
        feature.add_child(GenomicFeature('l3c', 'CDS', l3c))
        feature.add_child(GenomicFeature('l3d', 'CDS', l3d))
        feature['l3c'].add_child(GenomicFeature('l4a', 'CDS', l4a))
        feature['l3c'].add_child(GenomicFeature('l4b', 'CDS', l4b))

        self.assertEquals(seq[:5] + seq[25:30] + seq[40:60], feature.get_sub_seq(seq))
        self.assertEquals(seq[:5] + seq[25:30], feature['l3c'].get_sub_seq(seq))
        self.assertEquals(seq[40:60], feature['l3d'].get_sub_seq(seq))

    def test_pickling(self):
        l2b = Interval('1', 0, 100)
        l3c = Interval('1', 0, 30)
        l3d = Interval('1', 40, 60)
        l4a = Interval('1', 0, 5)
        l4b = Interval('1', 25, 30)
        feature = GenomicFeature('l2b', 'transcript', l2b)
        feature.add_child(GenomicFeature('l3c', 'CDS', l3c))
        feature.add_child(GenomicFeature('l3d', 'CDS', l3d))
        feature['l3c'].add_child(GenomicFeature('l4a', 'CDS', l4a))
        feature['l3c'].add_child(GenomicFeature('l4b', 'CDS', l4b))

        unpickled_feature = cPickle.loads(cPickle.dumps(feature))

        self.assertEquals('l2b', unpickled_feature.name)
        self.assertEquals({'l3c', 'l3d'}, set(child.name for child in unpickled_feature.children))


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
