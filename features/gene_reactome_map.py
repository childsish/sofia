from ebias.features import Feature, Resource

from collections import defaultdict

class GeneReactomeMap(Resource):

    EXT = ['.txt']
    OUT = ['gene_reactome_map']

    def init(self):
        fhndl = open(self.getFilename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            parts = line.strip().split('\t')
            self.parser[parts[0]].add(parts[1])
        fhndl.close()

class GetReactomeByGene(Feature):

    IN = ['gene_id', 'gene_reactome_map']
    OUT = ['reactome']

    def calculate(self, gene_id, gene_reactome_map):
        return gene_reactome_map[gene_id]

    def format(self, reactome):
        return ','.join(sorted(reactome))
