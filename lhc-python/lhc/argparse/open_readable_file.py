import argparse


class OpenReadableFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            from sys import stdin as fhndl
        else:
            fhndl = open(values)
        setattr(namespace, self.dest, fhndl)
