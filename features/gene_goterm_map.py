from sofia.features import Feature, Resource

from collections import defaultdict

class GeneGotermMap(Resource):

    EXT = ['.txt']
    OUT = ['gene_goterm_map']

    def init(self):
        fhndl = open(self.getFilename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            parts =[part.strip() for part in  line.split('\t')]
            self.parser[parts[0]].add((parts[1], parts[2]))
        fhndl.close()

class GetGotermByGene(Feature):
    
    IN = ['gene_id', 'gene_goterm_map']
    OUT = ['goterm']
    
    def init(self, domain=None):
        self.domain = domain
    
    def calculate(self, gene_id, gene_goterm_map):
        if self.domain is None:
            return set(goterm for goterm, domain in gene_goterm_map[gene_id]\
                if domain == self.domain)
        return set(goterm for goterm, domain in gene_goterm_map[gene_id])
    
    def format(self, goterm):
        return ','.join(sorted(goterm))
