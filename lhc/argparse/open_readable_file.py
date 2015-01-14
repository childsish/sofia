import argparse

from lhc.filetools.flexible_opener import open_flexibly


class OpenReadableFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            from sys import stdin as fhndl
        else:
            fname, fhndl = open_flexibly(values)
        setattr(namespace, self.dest, fhndl)
