import argparse
import struct

from Bio.bgzf import BgzfWriter, BgzfReader, _bgzf_magic, _bytes_BC, make_virtual_offset,\
    split_virtual_offset
from lhc.filetools.flexible_opener import open_flexibly


def get_virtual_offset(handle, offset, virtual_offset=0):
    """
    :param handle: the handle of a bgzip compressed file
    :param offset: the actual offset
    :param virtual_offset: find the virtual offset further along from this position
    :return: a virtual offset
    """
    block_start_offset, within_block_offset = split_virtual_offset(virtual_offset)
    handle.seek(block_start_offset)
    offset += within_block_offset
    while True:
        block_start_offset = handle.tell()
        magic = handle.read(4)
        if not magic:
            raise StopIteration
        if magic != _bgzf_magic:
            raise ValueError(r"A BGZF (e.g. a BAM file) block should start with "
                             r"%r, not %r; handle.tell() now says %r"
                             % (_bgzf_magic, magic, handle.tell()))
        gzip_mod_time, gzip_extra_flags, gzip_os, extra_len = \
            struct.unpack("<LBBH", handle.read(8))

        block_size = None
        x_len = 0
        while x_len < extra_len:
            subfield_id = handle.read(2)
            subfield_len = struct.unpack("<H", handle.read(2))[0]  # uint16_t
            subfield_data = handle.read(subfield_len)
            x_len += subfield_len + 4
            if subfield_id == _bytes_BC:
                assert subfield_len == 2, "Wrong BC payload length"
                assert block_size is None, "Two BC subfields?"
                block_size = struct.unpack("<H", subfield_data)[0] + 1  # uint16_t
        assert x_len == extra_len, (x_len, extra_len)
        assert block_size is not None, "Missing BC, this isn't a BGZF file!"
        handle.read(4)  # expected crc
        expected_size = struct.unpack("<I", handle.read(4))[0]
        if offset < expected_size:
            return make_virtual_offset(block_start_offset, offset)
        offset -= expected_size


def compress(input):
    fname, fhndl = open_flexibly(input, 'rb')
    if fname == 'stdin':
        raise ValueError('stdin disabled')
    writer = BgzfWriter('{}.bgz'.format(input))
    while True:
        data = fhndl.read(65536)
        writer.write(data)
        if not data:
            break
    fhndl.close()
    writer.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input')
    parser.set_defaults(func=lambda args: compress(args.input))
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
