from sofia.step import Step, EndOfStream


class GetGotermByGene(Step):
    
    IN = ['gene_id', 'gene_goterm_map']
    OUT = ['goterm']
    PARAMETERS = ['domain']
    
    def __init__(self, domain=None):
        self.domain = domain
    
    def run(self, ins, outs):
        gene_goterm_map = ins.gene_goterm_map.peek()
        while len(ins.gene_id) > 0:
            gene_id = ins.gene_id.pop()
            if gene_id is EndOfStream:
                outs.goterm.push(EndOfStream)
                return True

            goterm = None if gene_id is None else\
                set(goterm for goterm, domain in gene_goterm_map[gene_id]) if self.domain is None else\
                set(goterm for goterm, domain in gene_goterm_map[gene_id] if domain == self.domain)
            if not outs.goterm.push(goterm):
                break
        return len(ins.gene_id) == 0
