from sofia_.action import Resource

from collections import defaultdict


class GenePathwayMap(Resource):

    EXT = ['.txt']
    OUT = ['gene_pathway_map']

    def init(self):
        fhndl = open(self.getFilename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            gene_id, pathway_id = line.strip().split('\t')
            self.parser[gene_id].add(pathway_id)
        fhndl.close()


class GeneGotermMap(Resource):

    EXT = ['.txt']
    OUT = ['gene_goterm_map']

    def init(self):
        fhndl = open(self.getFilename())
        fhndl.next()
        self.parser = defaultdict(set)
        for line in fhndl:
            parts =[part.strip() for part in  line.split('\t')]
            self.parser[parts[0]].add((parts[1], parts[2]))
        fhndl.close()


class GeneIdIterator(Resource):

    EXT = ['.txt']
    OUT = ['gene_id']

    def init(self):
        fhndl = open(self.getFilename())
        self.parser = (line.strip() for line in fhndl.read().split('\n'))
        fhndl.close()

    def calculate(self):
        return self.parser.next()
