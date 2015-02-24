import argparse
import sys
import tempfile
import unittest

from lhc.argparse.open_writable_file import OpenWritableFile


class TestOpenWritableFile(unittest.TestCase):
    def test_default(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--output', action=OpenWritableFile, default=sys.stdout)
        args = parser.parse_args([])
        self.assertEquals(file, type(args.output))
        self.assertEquals('<stdout>', args.output.name)

    def test_provided(self):
        fhndl, fname = tempfile.mkstemp()
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--output', action=OpenWritableFile, default=sys.stdout)
        args = parser.parse_args('-o {}'.format(fname).split())
        self.assertEquals(file, type(args.output))
        self.assertEquals(fname, args.output.name)
        self.assertEquals('w', args.output.mode)

if __name__ == '__main__':
    sys.exit(unittest.main())