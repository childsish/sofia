from sofia.step import Step


class GetPathwayByGene(Step):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']

    def consume_input(self, input):
        copy = {
            'gene_id': input['gene_id'][:],
            'gene_pathway_map': input['gene_pathway_map'][0]
        }
        del input['gene_id'][:]
        return copy
    
    def run(self, gene_id, gene_pathway_map):
        for id_ in gene_id:
            yield gene_pathway_map[id_]
