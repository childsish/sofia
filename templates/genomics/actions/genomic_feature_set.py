from sofia_.action import Action


class GetGenomicFeatureByPosition(Action):
    
    IN = ['genomic_feature_set', 'genomic_position']
    OUT = ['genomic_feature']

    def calculate(self, genomic_feature_set, genomic_position):
        #TODO: select correct gene
        results = genomic_feature_set.fetch(
            genomic_position.chr,
            genomic_position.pos,
            genomic_position.pos + 1)
        if results is None or len(results) == 0:
            return None
        return results[0]


class GetGenomicFeatureByInterval(Action):
        
    IN = ['genomic_feature_set', 'genomic_interval']
    OUT = ['genomic_feature']

    def calculate(self, genomic_feature_set, genomic_interval):
        #TODO: select correct gene
        gene_model = genomic_feature_set.fetch(
            genomic_interval.chr,
            genomic_interval.start,
            genomic_interval.stop)
        if gene_model is None or len(gene_model) == 0:
            return None
        gene = gene_model[0]
        return {'gene_id': gene.name, 'chromosome_id': gene.chr, 'genomic_feature': gene}
