import unittest

from lhc.interval import Interval
from lhc.binf.genomic_coordinate import Interval as GenomicInterval
from lhc.io.txt_ import EntityParser, Entity, Column


class TestEntityParser(unittest.TestCase):
    def test_parse_entity(self):
        parser = EntityParser()

        row = ['2', '3', '4', 'test']

        self.assertEquals(4, parser.parse_definition('i2')(row))
        self.assertEquals('test', parser.parse_definition('s3')(row))
        self.assertEquals(Interval(2, 3), parser.parse_definition('r[i0,i1]')(row))

    def test_register_entity(self):
        parser = EntityParser()
        parser.register_type('gr', GenomicInterval)

        row = ['2', '3', '4', 'test']

        self.assertEquals(GenomicInterval('test', 2, 3), parser.parse_definition('gr[s3,i0,i1]')(row))

    def test_multiple_output(self):
        parser = EntityParser()

        entity_factory = parser.parse_definition('i0,test.i1,i2,s3')
        res = entity_factory(['2', '3', '4', 'test'])

        self.assertEquals(2, res[0])
        self.assertEquals(2, res.V1)
        self.assertEquals(3, res.test)

    def test_multiple_nested_output(self):
        parser = EntityParser()

        entity_factory = parser.parse_definition('r[i2,i3],f5')

        self.assertIsInstance(entity_factory.entities[0], Entity)
        self.assertIsInstance(entity_factory.entities[1], Column)
        self.assertEquals(float, entity_factory.entities[1].type)
        self.assertEquals(5, entity_factory.entities[1].column)
        self.assertIsInstance(entity_factory.entities[0].entities[0], Column)
        self.assertEquals(int, entity_factory.entities[0].entities[0].type)
        self.assertEquals(2, entity_factory.entities[0].entities[0].column)
        self.assertIsInstance(entity_factory.entities[0].entities[1], Column)
        self.assertEquals(int, entity_factory.entities[0].entities[1].type)
        self.assertEquals(3, entity_factory.entities[0].entities[1].column)


if __name__ == '__main__':
    unittest.main()
