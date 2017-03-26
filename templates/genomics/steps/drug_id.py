from sofia.step import Step


class DrugBankMap(Step):

    IN = ['drug_bank_map_file']
    OUT = ['drug_bank_map']

    def run(self, drug_bank_map_file):
        drug_bank_map_file = drug_bank_map_file[0]
        interface = {}
        fhndl = open(drug_bank_map_file, encoding='utf-8')
        fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            interface[parts[0]] = [part.strip() for part in parts[12].split(';')]
        fhndl.close()
        yield interface


class GetDrugIdFromDrugBank(Step):

    IN = ['drug_bank_map', 'transcript_id']
    OUT = ['drug_id']

    def consume_input(self, input):
        copy = {
            'drug_bank_map': input['drug_bank_map'][0],
            'transcript_id': input['transcript_id'][:]
        }
        del input['transcript_id'][:]
        return copy

    def run(self, drug_bank_map, transcript_id):
        for id_ in transcript_id:
            yield drug_bank_map.get(id_, None)


class GenomicsOfDrugSensitivityInCancerByGene(Step):

    IN = ['gdsc_map_file']
    OUT = ['gdsc_by_gene']

    def run(self, gdsc_map_file):
        gdsc_map_file = gdsc_map_file[0]
        interface = {}
        fhndl = open(gdsc_map_file, 'rU', encoding='utf-8')
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

    def consume_input(self, input):
        copy = {
            'gdsc_by_gene': input['gdsc_by_gene'][0],
            'gene_id': input['gene_id'][:]
        }
        del input['gene_id'][:]
        return copy

    def run(self, gdsc_by_gene, gene_id):
        for id_ in gene_id:
            yield gdsc_by_gene.get(id_, None)
