__author__ = 'Liam Childs'

import unittest

from lhc.indices.tbi import TabixIndex


class TestTabixIndex(unittest.TestCase):
    def test_fetch(self):
        tbi = TabixIndex('D:\\data\\public\\genomic_feature\\ref_GRCh37.p5_top_level.gff3.gz.tbi')
        tbi.fetch('NC_000001.10', 0, 10000)

if __name__ == '__main__':
    unittest.main()
