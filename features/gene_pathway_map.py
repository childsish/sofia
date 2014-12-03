from sofia_.features import Feature

class GetPathwayByGene(Feature):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']
    
    def calculate(self, gene_id, gene_pathway_map):
        return gene_pathway_map[gene_id]
    
    def format(self, pathway_id):
        return ','.join(sorted(pathway_id))
