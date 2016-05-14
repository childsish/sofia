import os
import tempfile
import unittest

from sofia_.subcommands.common import get_provided_entity


class TestCommonSubcommands(unittest.TestCase):
    def setUp(self):
        self.fileobj, self.filename = tempfile.mkstemp()
        os.close(self.fileobj)
        self.extensions = {'': 'tmp_file'}

    def test_get_provided_entity_filename_only(self):
        entity = get_provided_entity(self.filename, self.extensions)
        self.assertEqual('tmp_file', entity.name)
        self.assertEqual(self.filename, entity.attr['filename'])
        self.assertEqual(os.path.basename(self.filename), entity.alias)
        self.assertEqual({'filename': self.filename}, entity.attr)

    def test_get_provided_entity_filename_and_alias(self):
        definition = '{}:an_entity'.format(self.filename)
        entity = get_provided_entity(definition, self.extensions)
        self.assertEquals('tmp_file', entity.name)
        self.assertEquals('an_entity', entity.alias)
        self.assertEquals({'filename': self.filename}, entity.attr)

    def test_get_provided_entity_filename_and_entity(self):
        definition = '{}:entity=my_entity'.format(self.filename)
        entity = get_provided_entity(definition, self.extensions)
        self.assertEquals('my_entity', entity.name)
        self.assertEquals(os.path.basename(self.filename), entity.alias)
        self.assertEquals({'filename': self.filename}, entity.attr)

    def test_get_provided_entity_filename_alias_and_entity(self):
        definition = '{}:an_entity:entity=my_entity'.format(self.filename)
        entity = get_provided_entity(definition, self.extensions)
        self.assertEquals('my_entity', entity.name)
        self.assertEquals('an_entity', entity.alias)
        self.assertEquals({'filename': self.filename}, entity.attr)

    def test_get_provided_entity_entity_only(self):
        entity = get_provided_entity('my_entity', self.extensions)
        self.assertEqual('my_entity', entity.name)
        self.assertEqual('my_entity', entity.alias)
        self.assertEqual({}, entity.attr)

    def test_get_provided_entity_entity_and_alias(self):
        entity = get_provided_entity('my_entity:an_entity', self.extensions)
        self.assertEqual('my_entity', entity.name)
        self.assertEqual('an_entity', entity.alias)
        self.assertEqual({}, entity.attr)

    def test_get_provided_entity_entity_and_attribute(self):
        entity = get_provided_entity('my_entity:key=value', self.extensions)
        self.assertEqual('my_entity', entity.name)
        self.assertEqual('my_entity', entity.alias)
        self.assertEqual({'key': 'value'}, entity.attr)


    def tearDown(self):
        os.remove(self.filename)


if __name__ == '__main__':
    unittest.main()
