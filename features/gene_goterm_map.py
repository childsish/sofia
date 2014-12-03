from sofia_.features import Feature


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
