from sofia.step import Step, EndOfStream


class GetPathwayByGene(Step):
    
    IN = ['gene_id', 'gene_pathway_map']
    OUT = ['pathway_id']
    
    def run(self, ins, outs):
        gene_pathway_map = ins.gene_pathway_map.peek()
        while len(ins.gene_id) > 0:
            gene_id = ins.gene_id.pop()
            if gene_id is EndOfStream:
                outs.pathway_id.push(EndOfStream)
                return True

            pathway_id = gene_pathway_map.get(gene_id, None)
            if not outs.pathway_id.push(pathway_id):
                break
        return len(ins.gene_id) == 0
