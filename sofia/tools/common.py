import imp
import os

from sofia_.step import Step


def load_resource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: {}'.format(os.path.basename(fname)))


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def load_steps(step_directory):
    import os
    import sys

    format_error = 'Unable to import step {}. Parameter "format" is reserved and can not be used in attribute PARAMS.'

    steps = []
    sys.path.append(step_directory)
    for fname in os.listdir(step_directory):
        if fname.startswith('.') or not fname.endswith('.py'):
            continue
        module_name, ext = os.path.splitext(fname)
        module = imp.load_source(module_name, os.path.join(step_directory, fname))
        child_classes = [child_class for child_class in module.__dict__.itervalues()
                         if type(child_class) == type]
        for child_class in child_classes:
            if issubclass(child_class, Step) and child_class not in {Step}:
                if 'format' in child_class.PARAMS:
                    raise ImportError(format_error.format(child_class.__name__))
                steps.append(child_class)
    return steps
