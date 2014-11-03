from ebias.features import Feature

class GetPathwayByGene(Feature):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']
    
    def calculate(gene_id, gene_pathway_map):
        return gene_pathway_map[gene_id]
    
    def format(pathway_id):
        return ','.join(sorted(pathway_id))
