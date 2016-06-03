from sofia.step import Step


class RnaIterator(Step):

    IN = ['rna_file']
    OUT = ['rna_structure_iterator']

    def run(self, rna_file):
        raise NotImplementedError


class RnaSet(Step):

    IN = ['rna_structure']
    OUT = ['rna_structure_set']

    def run(self, rna_structure):
        raise NotImplementedError
