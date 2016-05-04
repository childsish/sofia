from sofia import Target


class RnaIterator(Target):

    EXT = {'.rna'}
    FORMAT = 'rna_file'
    OUT = ['rna_structure_iterator']

    def get_interface(self, filename):
        raise NotImplementedError


class RnaSet(Target):

    EXT = ['.rna']
    TYPE = 'rna_structure'
    OUT = ['rna_structure_set']

    def get_interface(self, filename):
        raise NotImplementedError
