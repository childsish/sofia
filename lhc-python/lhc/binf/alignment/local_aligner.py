from local_alignment import LocalAlignment
from scoring_matrix import ScoringMatrix

class LocalAligner(object):
    def __init__(self, scoring_matrix=None, gap_penalty=-1):
        if scoring_matrix is None:
            import numpy as np
            alphabet = 'acgtn_'
            mat = np.ones((len(alphabet), len(alphabet))) * -1
            for i in xrange(len(alphabet)):
                mat[i, i] = 1
                mat[i, 4] = 0
                mat[4, i] = 0
                mat[i, 5] = gap_penalty
                mat[5, i] = gap_penalty
            self.scoring_matrix = ScoringMatrix(alphabet, mat)

    def align(self, s1, s2):
        scoring_matrix = self.scoring_matrix
        scores = [0, 0, 0, 0]
        alignment = LocalAlignment(s1, s2)
        for i in xrange(1, len(s1) + 1):
            for j in xrange(1, len(s2) + 1):
                scores[1] = alignment.get_score(i, j - 1) +\
                    scoring_matrix['_', s2[j - 1]]
                scores[2] = alignment.get_score(i - 1, j) +\
                    scoring_matrix[s1[i - 1], '_']
                scores[3] = alignment.get_score(i - 1, j - 1) +\
                    scoring_matrix[s1[i - 1], s2[j - 1]]
                idx = scores.index(max(scores))
                alignment.set_score(i, j, scores[idx])
                alignment.set_pointer(i, j, idx)
        return alignment
