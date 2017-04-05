import argparse
import os
import re
import shutil
import tarfile
import tempfile
import zipfile

from urllib.request import urlopen

url_regx = re.compile('^https?://')


def get(filename, output):
    is_url = url_regx.match(filename)
    if is_url:
        filename = get_url(filename)
    get_file(filename, output)


def get_url(url):
    suffix = '.tar.gz' if url.endswith('.tar.gz') else\
        '.zip' if url.endswith('.zip') else\
        ''
    fileobj, filename = tempfile.mkstemp(suffix=suffix)
    os.write(fileobj, urlopen(url).read())
    os.close(fileobj)
    return filename


def get_file(filename, output):
    root = None
    if filename.endswith('.zip'):
        root = unzip(filename, output)
    elif filename.endswith('.tar.gz'):
        root = untar(filename, output)
    elif os.path.basename(filename) != output:
        root = filename
        shutil.copy(filename, output)

    if os.path.exists(os.path.join(output, root, 'resources.txt')):
        with open(os.path.join(output, root, 'resources.txt')) as fileobj:
            resource_lines = fileobj.readlines()
        with open(os.path.join(output, root, 'resources.txt'), 'w') as fileobj:
            for line in resource_lines:
                parts = line.split()
                parts[0] = os.path.join(output, root, parts[0])
                fileobj.write(' '.join(parts))
                fileobj.write('\n')


def unzip(filename, output):
    with zipfile.ZipFile(filename) as zip:
        root = zip.infolist()[0].filename
        zip.extractall(output)
        zip.close()
    return root


def untar(filename, output):
    with tarfile.open(filename) as tar:
        root = tar.getnames()[0]
        tar.extractall(output)
        tar.close()
    return root


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('input', nargs='*',
                        help='workflow template directory or compressed file (.tar.gz or .zip)')
    parser.add_argument('-o', '--output', default=os.getcwd(),
                        help='target directory to place workflow')
    parser.set_defaults(func=get_init)
    return parser


def get_init(args):
    inputs = [os.getcwd()] if args.input is None else args.input
    for input in inputs:
        get(input, args.output)

if __name__ == '__main__':
    import sys
    sys.exit(main())
