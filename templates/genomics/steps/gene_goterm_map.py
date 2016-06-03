from sofia.step import Step


class GetGotermByGene(Step):
    
    IN = ['gene_id', 'gene_goterm_map']
    OUT = ['goterm']
    PARAMETERS = ['domain']
    
    def __init__(self, domain=None):
        self.domain = domain
    
    def run(self, gene_id, gene_goterm_map):
        if self.domain is None:
            yield set(goterm for goterm, domain in gene_goterm_map[gene_id] if domain == self.domain)
        yield set(goterm for goterm, domain in gene_goterm_map[gene_id])
