import os


def iter_csv(fname, skip=0):
    it = iter_dir if os.path.isdir(fname) else iter_file
    return it(fname, column_builder, field_builder, skip)
