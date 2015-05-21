import unittest

from lhc.io.csv_.sort import CsvSorter


class TestSorter(unittest.TestCase):
    def test_below_max_lines_limit_no_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = CsvSorter(it)

        self.assertEquals(sorted(it), list(sorter))

    def test_above_max_lined_limit_no_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = CsvSorter(it, max_lines=20)

        self.assertEquals(sorted(it), list(sorter))

    def test_below_max_lines_limit_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = CsvSorter(it, key=lambda x: ord('z') - ord(x[0]))

        self.assertEquals(list(reversed(sorted(it))), list(sorter))

    def test_above_max_lines_limit_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = CsvSorter(it, max_lines=20, key=lambda x: ord('z') - ord(x[0]))

        self.assertEquals(list(reversed(sorted(it))), list(sorter))


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
