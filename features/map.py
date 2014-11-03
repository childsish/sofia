from ebias.features import Resource

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
