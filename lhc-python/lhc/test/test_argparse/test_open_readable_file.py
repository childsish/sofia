import argparse
import os
import sys
import tempfile
import unittest

from lhc.argparse.open_readable_file import OpenReadableFile


class TestOpenReadableFile(unittest.TestCase):
    def test_default(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input', action=OpenReadableFile, default=sys.stdin)
        args = parser.parse_args([])
        self.assertEquals(file, type(args.input))
        self.assertEquals('<stdin>', args.input.name)

    def test_provided(self):
        fhndl, fname = tempfile.mkstemp()
        os.close(fhndl)
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--output', action=OpenReadableFile, default=sys.stdout)
        args = parser.parse_args('-o {}'.format(fname).split())
        self.assertEquals(file, type(args.output))
        self.assertEquals(fname, args.output.name)
        self.assertEquals('r', args.output.mode)

if __name__ == '__main__':
    sys.exit(unittest.main())