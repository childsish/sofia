from sorted_dict import SortedDict


class StreamMerger(object):
    """ Merges several ordered iterators into one ordered iterator.
    """

    def __init__(self, iterators, key=None):
        """ Initialise the StreamMerger.

        :param iterators: The iterators to merge.
        :param key: A function that converts the iterator entries into comparable keys.
        :return: A StreamMerger
        """
        self.iterators = iterators
        self.key = (lambda x: x) if key is None else key

    def __iter__(self):
        """
        Iterate over the merged streams.

        :return: The entries of the merged stream
        """
        sorted_tops = SortedDict(key=self.key)
        tops = len(self.iterators) * [None]
        self._update_sorting(sorted_tops, tops, xrange(len(self.iterators)))
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.pop_lowest()
            for idx in idxs:
                yield tops[idx]
            self._update_sorting(sorted_tops, tops, idxs)

    def _update_sorting(self, sorted_tops, tops, idxs):
        """ Insert new entries into the merged stream.

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
