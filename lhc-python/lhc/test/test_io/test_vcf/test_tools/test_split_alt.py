__author__ = 'Liam Childs'

import unittest

from lhc.io.vcf_.iterator import Variant
from lhc.io.vcf_.tools.split_alt import _split_samples, _split_dict, _split_variant


class TestSplitAlt(unittest.TestCase):
    def test_split_dict(self):
        self.assertEquals(
            [
                {'DP': '1000', 'AO': '300'},
                {'DP': '1000', 'AO': '100'}
            ],
            _split_dict(
                {'DP': '1000', 'AO': '300,100'},
                2
            )
        )

        self.assertEquals(
            [
                {'DP': '1000', 'AO': '300', 'AF': '0.3'},
                {'DP': '1000', 'AO': '100', 'AF': '0.1'}
            ],
            _split_dict(
                {'DP': '1000', 'AO': '300,100', 'AF': '0.3,0.1'},
                2
            )
        )

    def test_split_samples(self):
        self.assertEquals(
            [
                {
                    's1': {'DP': '1000', 'AO': '300', 'AF': '0.3'},
                    's2': {'DP': '1000', 'AO': '400', 'AF': '0.4'}
                },
                {
                    's1': {'DP': '1000', 'AO': '100', 'AF': '0.1'},
                    's2': {'DP': '1000', 'AO': '200', 'AF': '0.2'}
                }
            ],
            _split_samples(
                {
                    's1': {'DP': '1000', 'AO': '300,100', 'AF': '0.3,0.1'},
                    's2': {'DP': '1000', 'AO': '400,200', 'AF': '0.4,0.2'}
                },
                2
            )
        )

    def test_split_variant(self):
        variant = Variant('1', 100, None, 'G', 'GAAC,C', None, None, {'f1': '0,1', 'f2': '3'}, {
            's1': {'DP': '1000', 'AO': '300,100', 'AF': '0.3,0.1'},
            's2': {'DP': '1000', 'AO': '400,200', 'AF': '0.4,0.2'}
        })

        v1, v2 = _split_variant(variant)

        self.assertEquals(Variant('1', 100, None, 'G', 'GAAC', None, None, {'f1': '0', 'f2': '3'}, {
            's1': {'DP': '1000', 'AO': '300', 'AF': '0.3'},
            's2': {'DP': '1000', 'AO': '400', 'AF': '0.4'}
        }), v1)
        self.assertEquals(Variant('1', 100, None, 'G', 'C', None, None, {'f1': '1', 'f2': '3'}, {
            's1': {'DP': '1000', 'AO': '100', 'AF': '0.1'},
            's2': {'DP': '1000', 'AO': '200', 'AF': '0.2'}
        }), v2)

    def test_split_variant_no_samples(self):
        variant = Variant('1', 100, None, 'G', 'GAAC,C', None, None, {'f1': '0,1', 'f2': '3'}, None)

        v1, v2 = _split_variant(variant)
        self.assertIsNone(v1.samples)
        self.assertIsNone(v2.samples)


if __name__ == '__main__':
    unittest.main()
