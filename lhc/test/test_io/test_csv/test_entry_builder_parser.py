import unittest

from lhc.interval import Interval
from lhc.binf.genomic_coordinate import Interval as GenomicInterval
from lhc.io.csv_ import EntryBuilderParser

def create_genomic_interval(chr, start, stop):
    return GenomicInterval(chr, int(start), int(stop))


class TestEntryBuilderParser(unittest.TestCase):
    def test_parse_entity(self):
        parser = EntryBuilderParser()

        row = ['2', '3', '4', 'test']

        self.assertEquals(4, parser.parse_entity('integer2')(row))
        self.assertEquals(4, parser.parse_entity('int2')(row))
        self.assertEquals(4, parser.parse_entity('i2')(row))
        self.assertEquals('test', parser.parse_entity('string3')(row))
        self.assertEquals('test', parser.parse_entity('str3')(row))
        self.assertEquals('test', parser.parse_entity('s3')(row))
        self.assertEquals(Interval(2, 3), parser.parse_entity('interval0,1')(row))
        self.assertEquals(Interval(2, 3), parser.parse_entity('v0,1')(row))

    def test_register_entity(self):
        parser = EntryBuilderParser()
        parser.register_type('genomic_interval', create_genomic_interval)
        parser.register_type('gv', create_genomic_interval)

        row = ['2', '3', '4', 'test']

        self.assertEquals(GenomicInterval('test', 2, 3), parser.parse_entity('genomic_interval3,0,1')(row))
        self.assertEquals(GenomicInterval('test', 2, 3), parser.parse_entity('gv3,0,1')(row))


if __name__ == '__main__':
    unittest.main()
