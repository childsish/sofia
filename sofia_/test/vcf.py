import unittest

from modules import vcf

class TestVcf(unittest.TestCase):
    def test_parseSamples(self):
        parts = ['GT:GQ:DP:HQ', '0|0:48:1:51,51', '1|0:48:8:51,51', '1/1:43:5:.,.']

        self.assertEquals(vcf.parseSamples(parts),
            [{'GT': '0|0', 'HQ': '51,51', 'DP': '1', 'GQ': '48'},
             {'GT': '1|0', 'HQ': '51,51', 'DP': '8', 'GQ': '48'},
             {'GT': '1/1', 'HQ': '.,.', 'DP': '5', 'GQ': '43'}])

if __name__ == "__main__":
    unittest.main()
