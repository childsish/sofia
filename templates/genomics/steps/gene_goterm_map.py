from sofia.step import Step


class GetGotermByGene(Step):
    
    IN = ['gene_id', 'gene_goterm_map']
    OUT = ['goterm']
    PARAMETERS = ['domain']
    
    def __init__(self, domain=None):
        self.domain = domain
    
    def run(self, gene_id, gene_goterm_map):
        gene_goterm_map = gene_goterm_map[0]
        for id_ in gene_id:
            if self.domain is None:
                yield set(goterm for goterm, domain in gene_goterm_map[id_] if domain == self.domain)
            yield set(goterm for goterm, domain in gene_goterm_map[id_])
        del gene_id[:]
