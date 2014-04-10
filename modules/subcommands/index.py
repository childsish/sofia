import os

from modules.resource import Resource
from common import loadPlugins, loadResource

def index(args):
    prog_dir = os.path.dirname(os.path.abspath(__file__))
    indir = os.path.join(prog_dir, 'resources')
    parsers = loadPlugins(indir, Resource)
    resource = loadResource(args.input, parsers, args.format)
    resource.index()
