from collections import defaultdict

from sofia import Resource


class GenePathwayMap(Resource):

    EXT = {'.txt'}
    FORMAT = 'gene_pathway_map'
    OUT = ['gene_pathway_map']

    def get_interface(self, filename):
        fhndl = open(filename)
        fhndl.next()
        res = defaultdict(set)
        for line in fhndl:
            gene_id, pathway_id = line.strip('\r\n').split('\t', 1)
            res[gene_id].add(pathway_id)
        fhndl.close()
        return res


class GeneGotermMap(Resource):

    EXT = {'.txt'}
    FORMAT = 'txt_file'
    OUT = ['gene_goterm_map']

    def get_interface(self, filename):
        fhndl = open(filename)
        fhndl.next()
        res = defaultdict(set)
        for line in fhndl:
            parts = [part.strip() for part in line.split('\t')]
            res[parts[0]].add((parts[1], parts[2]))
        fhndl.close()
        return res
