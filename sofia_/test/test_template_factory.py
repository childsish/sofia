import os
import unittest

from sofia_.step import Step, Resource
from sofia_.template_factory import TemplateFactory, inherits_from


class TestTemplateFactory(unittest.TestCase):
    def test_init(self):
        path = os.path.join(__file__[:__file__.rfind('sofia_')], 'templates', 'genomics')
        factory = TemplateFactory(path)

        self.assertTrue(all(inherits_from(step, 'Step') for step in factory.steps))
        self.assertEqual(20, sum(inherits_from(step, 'Resource') for step in factory.steps))


if __name__ == '__main__':
    unittest.main()
