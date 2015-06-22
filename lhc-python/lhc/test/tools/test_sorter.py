import unittest

from lhc.io.txt_.tools.sort import Sorter


class TestSorter(unittest.TestCase):
    def test_below_max_lines_limit_no_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = Sorter()

        self.assertEquals(sorted(it), list(sorter.sort(it)))

    def test_above_max_lined_limit_no_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = Sorter(max_lines=20)

        self.assertEquals(sorted(it), list(sorter.sort(it)))

    def test_below_max_lines_limit_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = Sorter(key=lambda x: ord('z') - ord(x[0]))

        self.assertEquals(list(reversed(sorted(it))), list(sorter.sort(it)))

    def test_above_max_lines_limit_key(self):
        it = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        it = ['{}\n'.format(x) for x in it]
        sorter = Sorter(max_lines=20, key=lambda x: ord('z') - ord(x[0]))

        self.assertEquals(list(reversed(sorted(it))), list(sorter.sort(it)))


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
