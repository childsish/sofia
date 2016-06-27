from sofia.step import Step


class DrugBankMap(Step):

    IN = ['drug_bank_map_file']
    OUT = ['drug_bank_map']

    def run(self, drug_bank_map_file):
        drug_bank_map_file = drug_bank_map_file.pop()
        interface = {}
        fhndl = open(drug_bank_map_file)
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
        drug_bank_map = drug_bank_map[0]
        for id_ in transcript_id:
            yield drug_bank_map.get(id_, None)
        del transcript_id[:]


class GenomicsOfDrugSensitivityInCancerByGene(Step):

    IN = ['gdsc_map_file']
    OUT = ['gdsc_by_gene']

    def run(self, gdsc_map_file):
        gdsc_map_file = gdsc_map_file.pop()
        interface = {}
        fhndl = open(gdsc_map_file, 'rU')
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
        gdsc_by_gene = gdsc_by_gene[0]
        for id_ in gene_id:
            yield gdsc_by_gene.get(id_, None)
        del gene_id[:]
