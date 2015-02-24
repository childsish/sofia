from lhc.collections.sorted_dict import SortedDict


class SortedIteratorMerger(object):
    """ Merges several sorted iterators into one sorted iterator.
    """

    def __init__(self, iterators, key=None):
        """ Initialise the SortedIteratorMerger.

        :param iterators: The iterators to merge.
        :param key: A function that converts the iterator entries into comparable keys.
        :return: A SortedIteratorMerger
        """
        n_iterators = len(iterators)
        self.iterators = iterators
        self.sorted_tops = SortedDict()
        self.tops = n_iterators * [None]
        self.idxs = range(n_iterators)
        self.c_idx = 0
        self.key = (lambda x: x) if key is None else key

        self._update_sorting()

    def __iter__(self):
        return self

    def next(self):
        if self.c_idx == len(self.idxs):
            self._update_sorting()
        res = self.tops[self.idxs[self.c_idx]]
        self.c_idx += 1
        return res

    def close(self):
        """
        Closes all the iterators.

        This is particularly important if the iterators are files.
        """
        if hasattr(self, 'iterators'):
            for it in self.iterators:
                if hasattr(it, 'close'):
                    it.close()

    def _update_sorting(self):
        """ Insert new entries into the merged iterator.

        :param sorted_tops: A SortedDict.
        :param tops: The most recent entry from each iterator.
        :param idxs: The indices to update.
        """
        key = self.key
        sorted_tops = self.sorted_tops
        tops = self.tops
        iterators = self.iterators
        for idx in self.idxs:
            try:
                tops[idx] = iterators[idx].next()
                top_key = key(tops[idx])
                if top_key not in sorted_tops:
                    sorted_tops[top_key] = []
                sorted_tops[top_key].append(idx)
            except StopIteration:
                pass
        if len(sorted_tops) == 0:
            raise StopIteration
        key, self.idxs = sorted_tops.pop_lowest()
        self.c_idx = 0
