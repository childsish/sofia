__author__ = 'Liam Childs'

import bisect
import random


class SequenceGenerator(object):

    NUCLEOTIDES = (('A', 1), ('C', 1), ('G', 1), ('T', 1))
    AMINO_ACIDS = (('A', 1), ('C', 1), ('D', 1), ('E', 1), ('F', 1), ('G', 1), ('H', 1), ('I', 1), ('K', 1), ('L', 1),
                   ('M', 1), ('N', 1), ('P', 1), ('Q', 1), ('R', 1), ('S', 1), ('T', 1), ('V', 1), ('W', 1), ('Y', 1))

    def __init__(self, letters=None):
        """ Create a sequence generator that can generate sequences with given letter frequencies

        :param letters: letters and probabilities as a list of (letter, weight) tuples.
        """
        if letters is None:
            letters = self.NUCLEOTIDES
        self.letters, weights = zip(*letters)
        self.cumulative_distribution = self._get_cumulative_distribution(weights)

    def generate(self, length):
        return ''.join(self._get_letter() for i in xrange(length))

    def _get_cumulative_distribution(self, weights):
        total_weight = float(sum(weights))
        probabilities = [weight / total_weight for weight in weights]
        return list(cumsum(probabilities))

    def _get_letter(self):
        quantile = random.random()
        return self.letters[bisect.bisect(self.cumulative_distribution, quantile)]


def cumsum(iterable):
    running_total = 0
    for item in iterable:
        running_total += item
        yield running_total
