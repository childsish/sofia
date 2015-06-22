__author__ = 'Liam Childs'

from Bio.bgzf import BgzfWriter


class Compressor(object):
    def __init__(self, block_size=65536, block_delimiter='\n'):
        self.block_size = block_size
        self.block_delimiter = block_delimiter

    def compress(self, input, output):
        if not isinstance(output, BgzfWriter):
            output = BgzfWriter(fileobj=output)

        if self.block_delimiter is None:
            self.compress_without_delimiter(input, output)
        else:
            self.compress_with_delimiter(input, output)

    def compress_without_delimiter(self, input, output):
        block_size = self.block_size

        data = ''
        while True:
            data += input.read(block_size)
            if not data:
                break
            output.write(data)

    def compress_with_delimiter(self, input, output):
        block_size = self.block_size
        block_delimiter = self.block_delimiter

        data = ''
        while True:
            data += input.read(block_size - len(data))
            if not data:
                break
            idx = data.rfind(block_delimiter)
            output.write(data[:idx])
            output.flush()
            data = data[idx:]
