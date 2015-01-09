import argparse


class OpenWritableFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            from sys import stdout as fhndl
        else:
            fhndl = open(values, 'w')
        setattr(namespace, self.dest, fhndl)
