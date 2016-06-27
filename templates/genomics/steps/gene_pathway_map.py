from sofia.step import Step


class GetPathwayByGene(Step):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']
    
    def run(self, gene_id, gene_pathway_map):
        gene_pathway_map = gene_pathway_map[0]
        for id_ in gene_id:
            yield gene_pathway_map[id_]
        del gene_id[:]
