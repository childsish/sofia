import os
import tempfile
import unittest

from lhc.io.csv_ import BuilderGuesser


class TestBuilderGuesser(unittest.TestCase):
    def test_guess_type(self):
        fhndl, fname = tempfile.mkstemp()
        os.write(fhndl, 'a\tb\tc\td\n')
        os.close(fhndl)

        guesser = BuilderGuesser()
        builder = guesser.guess_type(fname)

        self.assertEquals(('V1', 'V2', 'V3', 'V4'), builder.type._fields)
        self.assertEquals([0, 1, 2, 3], [column.column for column in builder.entities])


if __name__ == '__main__':
    unittest.main()
