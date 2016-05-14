import unittest

from collections import namedtuple
from sofia_.converter import Converter

TestObject = namedtuple('TestObject', ('a', 'b'))


class TestConverter(unittest.TestCase):
    def test_convert(self):
        entity = TestObject(a={'x': 'id_0'}, b=1)
        path = [{'key': 'a', 'type': 'attr'}, {'key': 'x', 'type': 'item'}]
        id_map = {'id_0': 'id_1'}
        converter = Converter(path=path, id_map=id_map)

        res = converter.convert(entity)
        self.assertEquals('id_1', res.a['x'])


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
