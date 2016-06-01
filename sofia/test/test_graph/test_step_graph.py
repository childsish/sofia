__author__ = 'Liam Childs'

import unittest

from sofia.step import Step
from sofia.workflow_template import Workflow


class TestStepGraph(unittest.TestCase):
    def test_init(self):
        graph = Workflow(Step(name='s1'))

        self.assertIn('s1', graph.steps)
        self.assertIn('s1', graph.graph.vs)
        self.assertEquals('Step', graph.graph.name)

    def test_update(self):
        s1 = Workflow(Step(name='s1'))
        s2 = Workflow(Step(name='s2'))
        s3 = Workflow(Step(name='s3'))

        s2.add_resource('r1')
        s2.join(s1, 'e1')
        s3.join(s2, 'e2')

        self.assertEquals({'s1', 's2', 's3'}, set(s3.steps))
        self.assertEquals({'r1'}, s3.resources)


if __name__ == '__main__':
    unittest.main()
