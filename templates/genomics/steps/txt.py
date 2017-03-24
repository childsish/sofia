from collections import defaultdict

from sofia.step import Step


class GenePathwayMap(Step):

    IN = ['gene_pathway_map_file']
    OUT = ['gene_pathway_map']

    def run(self, gene_pathway_map_file):
        gene_pathway_map_file = gene_pathway_map_file[0]
        fhndl = open(gene_pathway_map_file, encoding='utf-8')
        fhndl.next()
        res = defaultdict(set)
        for line in fhndl:
            gene_id, pathway_id = line.strip('\r\n').split('\t', 1)
            res[gene_id].add(pathway_id)
        fhndl.close()
        yield res


class GeneGotermMap(Step):

    IN = ['gene_goterm_map_file']
    OUT = ['gene_goterm_map']

    def run(self, gene_goterm_map_file):
        gene_goterm_map_file = gene_goterm_map_file[0]
        fhndl = open(gene_goterm_map_file, encoding='utf-8')
        fhndl.next()
        res = defaultdict(set)
        for line in fhndl:
            parts = [part.strip() for part in line.split('\t')]
            res[parts[0]].add((parts[1], parts[2]))
        fhndl.close()
        yield res
