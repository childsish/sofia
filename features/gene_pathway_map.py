from sofia_.features import Feature, Resource

from collections import defaultdict

class GenePathwayMap(Resource):

    EXT = ['.txt']
    OUT = ['gene_pathway_map']

    def init(self):
        fhndl = open(self.getFilename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            gene_id, pathway_id = line.strip().split('\t')
            self.parser[gene_id].add(pathway_id)
        fhndl.close()

class GetPathwayByGene(Feature):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']
    
    def calculate(self, gene_id, gene_pathway_map):
        return gene_pathway_map[gene_id]
    
    def format(self, pathway_id):
        return ','.join(sorted(pathway_id))
