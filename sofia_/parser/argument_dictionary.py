import argparse


class ArgumentDictionary(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        setattr(namespace, self.dest, dict(v.split('=', 1) for v in values))
