from sofia_.step import Resource, Target

from collections import defaultdict


class GenePathwayMap(Resource):

    EXT = {'.txt'}
    FORMAT = 'gene_pathway_map'
    OUT = ['gene_pathway_map']

    def init(self):
        fhndl = open(self.get_filename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            gene_id, pathway_id = line.strip('\r\n').split('\t')
            self.parser[gene_id].add(pathway_id)
        fhndl.close()


class GeneGotermMap(Resource):

    EXT = {'.txt'}
    FORMAT = 'txt'
    OUT = ['gene_goterm_map']

    def init(self):
        fhndl = open(self.get_filename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            parts = [part.strip() for part in line.split('\t')]
            self.parser[parts[0]].add((parts[1], parts[2]))
        fhndl.close()
