from sofia_.step import Step, Resource


class DrugBankMap(Resource):

    FORMAT = 'drug_bank_map'
    OUT = ['drug_bank_map']

    def get_interface(self, filename):
        interface = {}
        fhndl = open(filename)
        fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            interface[parts[0]] = [part.strip() for part in parts[12].split(';')]
        fhndl.close()
        return interface


class GetDrugIdFromDrugBank(Step):

    IN = ['drug_bank_map', 'transcript_id']
    OUT = ['drug_id']

    def calculate(self, drug_bank_map, transcript_id):
        return drug_bank_map[transcript_id] if transcript_id in drug_bank_map else None


class GenomicsOfDrugSensitivityInCancerByGene(Resource):

    FORMAT = 'gdsc_map'
    OUT = ['gdsc_by_gene']

    def get_interface(self, filename):
        interface = {}
        fhndl = open(filename)
        fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            genes = parts[0].split('///')
            for gene in genes:
                interface[gene.strip()] = parts[2]
        fhndl.close()
        return interface


class GetDrugIdFromGDSC(Step):

    IN = ['gdsc_by_gene', 'gene_id']
    OUT = ['drug_id']

    def calculate(self, gdsc_by_gene, gene_id):
        return gdsc_by_gene[gene_id] if gene_id in gdsc_by_gene else None
