import os
import tempfile
import unittest

from sofia_.step.resource import Resource, Target
from sofia_.parser.provided_resource import ProvidedResource


class SampleResource(Resource):

    EXT = {'.abc', '.def'}
    FORMAT = 'sample_resource'


class TestResource(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        for fname in ('resource.abc', 'resource.ghi'):
            fhndl = open(os.path.join(self.dir, fname), 'w')
            fhndl.write('\n')
            fhndl.close()

    def test_matches(self):
        r1 = ProvidedResource(os.path.join(self.dir, 'resource.abc'))
        r2 = ProvidedResource(os.path.join(self.dir, 'resource.ghi'))
        r3 = ProvidedResource(os.path.join(self.dir, 'resource.abc'), format='sample_resource')
        r4 = ProvidedResource(os.path.join(self.dir, 'resource.ghi'), format='sample_resource')
        r5 = ProvidedResource(os.path.join(self.dir, 'resource.abc'), format='not_sample_resource')
        r6 = ProvidedResource(os.path.join(self.dir, 'resource.ghi'), format='not_sample_resource')

        self.assertTrue(SampleResource.matches(r1))
        self.assertFalse(SampleResource.matches(r2))
        self.assertTrue(SampleResource.matches(r3))
        self.assertTrue(SampleResource.matches(r4))
        self.assertFalse(SampleResource.matches(r5))
        self.assertFalse(SampleResource.matches(r6))

    def tearDown(self):
        for fname in ('resource.abc', 'resource.ghi'):
            os.remove(os.path.join(self.dir, fname))
        os.rmdir(self.dir)


class TestTarget(unittest.TestCase):
    pass

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
