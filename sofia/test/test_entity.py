import unittest

from sofia_.entity_type import EntityType


class TestEntity(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(EntityType('x'), EntityType('x'))
        self.assertNotEqual(EntityType('x'), EntityType('y'))
        self.assertEqual(EntityType('x', resources={'target', 'resource1'}),
                         EntityType('x', resources={'resource1', 'target'}))
        self.assertNotEqual(EntityType('x', resources={'target'}),
                            EntityType('x', resources={'test'}))
        self.assertEqual(EntityType('x', attributes={'key1': 'value1', 'key2': 'value2'}),
                         EntityType('x', attributes={'key2': 'value2', 'key1': 'value1'}))
        self.assertNotEqual(EntityType('x', attributes={'key1': 'value1', 'key2': 'value2'}),
                            EntityType('x', attributes={'key1': 'value1', 'key3': 'value3'}))


if __name__ == '__main__':
    unittest.main()
