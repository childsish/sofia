__author__ = 'Liam Childs'

import unittest
import os
import tempfile

from sofia_.parser.resource_parser import ResourceParser


class TestResourceParser(unittest.TestCase):
    def setUp(self):
        self.hndl, self.name = tempfile.mkstemp()
        os.close(self.hndl)
        self.parser = ResourceParser()

    def test_parse_resource_basic(self):
        resource = self.parser.parse_resource(self.name)

        self.assertEqual(self.name, resource.fname)
        self.assertEqual(os.path.basename(self.name), resource.name)

    def test_parse_resource_name(self):
        resource_string = '{}:test'.format(self.name)
        resource = self.parser.parse_resource(resource_string)

        self.assertEqual(self.name, resource.fname)
        self.assertEqual('test', resource.name)

    def test_parse_resource_attribute(self):
        resource_string = '{}:x=x'.format(self.name)
        resource = self.parser.parse_resource(resource_string)

        self.assertEqual(self.name, resource.fname)
        self.assertEqual(os.path.basename(self.name), resource.name)
        self.assertEqual({'x': ['x']}, resource.attr)

    def test_parse_resource_name_attribute(self):
        resource_string = '{}:test:x=x'.format(self.name)
        resource = self.parser.parse_resource(resource_string)

        self.assertEqual(self.name, resource.fname)
        self.assertEqual('test', resource.name)
        self.assertEqual({'x': ['x']}, resource.attr)

    def test_parse_resource_attribute_name(self):
        resource_string = '{}:x=x:test'.format(self.name)
        resource = self.parser.parse_resource(resource_string)

        self.assertEqual(self.name, resource.fname)
        self.assertEqual('test', resource.name)
        self.assertEqual({'x': ['x']}, resource.attr)


if __name__ == '__main__':
    unittest.main()
