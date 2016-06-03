from sofia.step import Step


class DrugBankMap(Step):

    FORMAT = 'drug_bank_map'
    OUT = ['drug_bank_map']

    def run(self, filename):
        interface = {}
        fhndl = open(filename)
        fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            interface[parts[0]] = [part.strip() for part in parts[12].split(';')]
        fhndl.close()
        yield interface


class GetDrugIdFromDrugBank(Step):

    IN = ['drug_bank_map', 'transcript_id']
    OUT = ['drug_id']

    def run(self, drug_bank_map, transcript_id):
        yield drug_bank_map[transcript_id] if transcript_id in drug_bank_map else None


class GenomicsOfDrugSensitivityInCancerByGene(Step):

    FORMAT = 'gdsc_map'
    OUT = ['gdsc_by_gene']

    def run(self, filename):
        interface = {}
        fhndl = open(filename, 'rU')
        line = fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            genes = parts[0].split('///')
            for gene in genes:
                interface[gene.strip()] = parts[2]
        fhndl.close()
        yield interface


class GetDrugIdFromGDSC(Step):

    IN = ['gdsc_by_gene', 'gene_id']
    OUT = ['drug_id']

    def run(self, gdsc_by_gene, gene_id):
        yield gdsc_by_gene[gene_id] if gene_id in gdsc_by_gene else None
