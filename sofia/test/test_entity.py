import unittest

from sofia import Entity


class TestEntity(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(Entity('x'), Entity('x'))
        self.assertNotEqual(Entity('x'), Entity('y'))
        self.assertEqual(Entity('x', resources={'target', 'resource1'}),
                         Entity('x', resources={'resource1', 'target'}))
        self.assertNotEqual(Entity('x', resources={'target'}),
                            Entity('x', resources={'test'}))
        self.assertEqual(Entity('x', attr={'key1': 'value1', 'key2': 'value2'}),
                         Entity('x', attr={'key2': 'value2', 'key1': 'value1'}))
        self.assertNotEqual(Entity('x', attr={'key1': 'value1', 'key2': 'value2'}),
                            Entity('x', attr={'key1': 'value1', 'key3': 'value3'}))


if __name__ == '__main__':
    unittest.main()
