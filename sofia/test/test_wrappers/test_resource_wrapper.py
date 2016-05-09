import os
import tempfile
import unittest

from sofia.entity import Entity
from sofia.wrappers.resource_wrapper import ResourceWrapper


class SampleResource(ResourceWrapper):

    IN = []
    OUT = ['sample_entity']
    EXT = {'.abc', '.def'}
    FORMAT = 'sample_resource'


class TestResourceWrapper(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        for fname in ('resource.abc', 'resource.ghi'):
            fhndl = open(os.path.join(self.dir, fname), 'w')
            fhndl.write('\n')
            fhndl.close()

    def test_matches(self):
        wrapper = ResourceWrapper(SampleResource)

        r1 = Entity(None, {'test'}, {'filename': os.path.join(self.dir, 'resource.abc')}, 'test')
        r2 = Entity(None, {'test'}, {'filename': os.path.join(self.dir, 'resource.ghi')}, 'test')
        r3 = Entity('sample_resource', {'test'}, {'filename': os.path.join(self.dir, 'resource.abc')}, 'test')
        r4 = Entity('sample_resource', {'test'}, {'filename': os.path.join(self.dir, 'resource.ghi')}, 'test')
        r5 = Entity('not_sample_resource', {'test'}, {'filename': os.path.join(self.dir, 'resource.abc')}, 'test')
        r6 = Entity('not_sample_resource', {'test'}, {'filename': os.path.join(self.dir, 'resource.ghi')}, 'test')

        self.assertTrue(wrapper.matches(r1))
        self.assertFalse(wrapper.matches(r2))
        self.assertTrue(wrapper.matches(r3))
        self.assertTrue(wrapper.matches(r4))
        self.assertFalse(wrapper.matches(r5))
        self.assertFalse(wrapper.matches(r6))

    def tearDown(self):
        for fname in ('resource.abc', 'resource.ghi'):
            os.remove(os.path.join(self.dir, fname))
        os.rmdir(self.dir)


class TestTarget(unittest.TestCase):
    pass

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())