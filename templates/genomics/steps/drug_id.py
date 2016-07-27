from sofia.step import Step, EndOfStream


class DrugBankMap(Step):

    IN = ['drug_bank_map_file']
    OUT = ['drug_bank_map']

    def run(self, ins, outs):
        while len(ins) > 0:
            drug_bank_map_file = ins.drug_bank_map_file.pop()
            if drug_bank_map_file is EndOfStream:
                outs.drug_bank_map.push(EndOfStream)
                return True

            drug_bank_map = None if drug_bank_map_file is None else self.get_drug_bank_map(drug_bank_map_file)
            if not outs.drug_bank_map.push(drug_bank_map):
                break
        return len(ins) == 0

    def get_drug_bank_map(self, filename):
        interface = {}
        fhndl = open(filename)
        fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            interface[parts[0]] = [part.strip() for part in parts[12].split(';')]
        fhndl.close()
        return interface


class GetDrugIdFromDrugBank(Step):

    IN = ['transcript_id', 'drug_bank_map']
    OUT = ['drug_id']

    def run(self, ins, outs):
        drug_bank_map = ins.drug_bank_map.peek()
        while len(ins.transcript_id) > 0:
            transcript_id = ins.transcript_id.pop()
            if transcript_id is EndOfStream:
                outs.drug_id.push(EndOfStream)
                return True

            drug_id = None if transcript_id is None else drug_bank_map.get(transcript_id, None)
            if not outs.drug_id.push(drug_id):
                break
        return len(ins.transcript_id) == 0


class GenomicsOfDrugSensitivityInCancerByGene(Step):

    IN = ['gdsc_map_file']
    OUT = ['gdsc_by_gene']

    def run(self, ins, outs):
        while len(ins) > 0:
            gdsc_map_file = ins.gdsc_map_file.pop()
            if gdsc_map_file is EndOfStream:
                outs.gdsc_by_gene.push(EndOfStream)
                return True

            gdsc_by_gene = None if gdsc_map_file is None else self.get_gdsc_by_gene(gdsc_map_file)
            if not outs.gdsc_by_gene.push(gdsc_by_gene):
                break
        return len(ins) == 0

    def get_gdsc_by_gene(self, filename):
        interface = {}
        fhndl = open(filename, 'rU')
        line = fhndl.next()
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

    def run(self, ins, outs):
        gdsc_by_gene = ins.gdsc_by_gene.peek()
        while len(ins.gene_id) > 0:
            gene_id = ins.gene_id.pop()
            if gene_id is EndOfStream:
                outs.drug_id.push(EndOfStream)
                return True

            drug_id = None if gene_id is None else gdsc_by_gene.get(gene_id, None)
            if not outs.gene_id.push(drug_id):
                break
        return len(ins.gene_id) == 0
