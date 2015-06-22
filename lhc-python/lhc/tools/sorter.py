import cPickle
import os

from itertools import chain
from lhc.itertools import ChunkedIterator, SortedIteratorMerger

class Sorter(object):

    TMP_FNAME = '{}.txt'

    def __init__(self, key=None, max_lines=1000000):
        self.key = key
        self.max_lines = max_lines

    def sort(self, iterator):
        iterator = ChunkedIterator(iterator, self.max_lines)
        return self._get_sorted_iterator(iterator)

    def _get_sorted_iterator(self, iterator):
        """
        Get the iterator over the sorted items.

        This function decides whether the items can be sorted in memory or on disk.
        :return:
        """
        lines = list(iterator.next())
        if len(lines) < self.max_lines:
            return iter(sorted(lines, key=self.key))

        import tempfile
        tmp_dir = tempfile.mkdtemp()
        fnames = self._split(chain([lines], iterator), tmp_dir)
        return SortedIteratorMerger([unpickle_iter(open(fname)) for fname in fnames], self.key)

    def _split(self, iterator, tmp_dir):
        """
        Splits the file into several chunks.

        If the original file is too big to fit in the allocated space, the sorting will be split into several chunks,
        then merged.
        :param tmp_dir: Where to put the intermediate sorted results.
        :param orig_lines: The lines read before running out of space.
        :return: The names of the intermediate files.
        """
        fnames = []
        for i, lines in enumerate(iterator):
            lines = list(lines)
            out_fname = os.path.join(tmp_dir, self.TMP_FNAME.format(i + 1))
            self._write(lines, out_fname)
            fnames.append(out_fname)
            if len(lines) < self.max_lines:
                break
        return fnames

    def _write(self, lines, fname):
        """
        Writes a intermediate temporary sorted file

        :param lines: The lines to write.
        :param fname: The name of the temporary file.
        :return:
        """
        out_fhndl = open(fname, 'wb')
        for line in sorted(lines, key=self.key):
            cPickle.dump(line, out_fhndl)
        out_fhndl.close()

def unpickle_iter(fileobj):
    try:
        while True:
             yield cPickle.load(fileobj)
    except EOFError:
        raise StopIteration
