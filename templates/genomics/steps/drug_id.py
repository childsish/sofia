from sofia_.step import Step, Resource


class DrugBankMap(Resource):

    FORMAT = 'drug_bank_map'
    OUT = ['drug_bank_map']

    def get_interface(self, filename):
        res = {}
        fhndl = open(filename)
        fhndl.next()
        for line in fhndl:
            parts = line.rstrip('\r\n').split(',')
            res[parts[0]] = [part.strip() for part in parts[12].split(';')]
        fhndl.close()
        return res


class GetDrugIdFromDrugBank(Step):

    IN = ['drug_bank_map', 'transcript_id']
    OUT = ['drug_id']

    def calculate(self, drug_bank_map, transcript_id):
        return drug_bank_map[transcript_id] if transcript_id in drug_bank_map else None
