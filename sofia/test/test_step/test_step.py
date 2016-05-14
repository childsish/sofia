__author__ = 'Liam Childs'

import unittest

from sofia.step import Step


class TestStep(unittest.TestCase):
    def test_get_output(self):
        step = Step()

        self.assertEquals('OrderedDict', type(step.get_output()).__name__)


if __name__ == '__main__':
    unittest.main()
