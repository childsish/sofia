class ScoringMatrix(object):
    def __init__(self, characters, matrix):
        self.character_map = {k: i for i, k in enumerate(characters)}
        self.matrix = matrix
    
    def __getitem__(self, key):
        c1, c2 = key
        return self.matrix[self.character_map[c1], self.character_map[c2]]
