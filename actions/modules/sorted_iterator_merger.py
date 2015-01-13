from sorted_dict import SortedDict


class SortedIteratorMerger(object):
    """ Merges several sorted iterators into one sorted iterator.
    """

    def __init__(self, iterators, key=None):
        """ Initialise the SortedIteratorMerger.

        :param iterators: The iterators to merge.
        :param key: A function that converts the iterator entries into comparable keys.
        :return: A SortedIteratorMerger
        """
        self.iterators = iterators
        self.key = (lambda x: x) if key is None else key

    def __iter__(self):
        """
        Iterate over the merged iterators.

        :return: The entries of the merged iterator
        """
        sorted_tops = SortedDict(key=self.key)
        tops = len(self.iterators) * [None]
        self._update_sorting(sorted_tops, tops, xrange(len(self.iterators)))
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.pop_lowest()
            for idx in idxs:
                yield tops[idx]
            self._update_sorting(sorted_tops, tops, idxs)

    def close(self):
        """
        Closes all the iterators.

        This is particularly important if the iterators are files.
        """
        if hasattr(self, 'iterators'):
            for it in self.iterators:
                if hasattr(it, 'close'):
                    it.close()

    def _update_sorting(self, sorted_tops, tops, idxs):
        """ Insert new entries into the merged iterator.

        :param sorted_tops: A SortedDict.
        :param tops: The most recent entry from each iterator.
        :param idxs: The indices to update.
        """
        for idx in idxs:
            try:
                tops[idx] = self.iterators[idx].next()
                sorted_tops.get(tops[idx], []).append(idx)
            except StopIteration:
                pass
