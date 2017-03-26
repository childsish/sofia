import os
import unittest

from sofia.workflow_template.load_template import TemplateFactory, inherits_from


class TestTemplateFactory(unittest.TestCase):
    def test_init(self):
        path = os.path.join(__file__[:__file__.rfind('sofia')], 'templates', 'genomics')
        factory = TemplateFactory(path)

        self.assertTrue(all(inherits_from(step, 'Step') for step in factory.steps))
        self.assertEqual(22, sum(inherits_from(step, 'Resource') for step in factory.steps))


if __name__ == '__main__':
    unittest.main()
