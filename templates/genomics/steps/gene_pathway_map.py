from sofia.step import Step


class GetPathwayByGene(Step):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']
    
    def run(self, gene_id, gene_pathway_map):
        yield gene_pathway_map[gene_id]
