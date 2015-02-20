from sofia_.action import Action


class GetGenomicFeatureByPosition(Action):
    
    IN = ['genomic_feature_set', 'genomic_position']
    OUT = ['genomic_feature']

    def calculate(self, genomic_feature_set, genomic_position):
        #TODO: select correct gene
        results = genomic_feature_set.fetch(
            genomic_position['chromosome_id'],
            genomic_position['chromosome_pos'],
            genomic_position['chromosome_pos'] + 1)
        if results is None or len(results) == 0:
            return None
        genomic_feature = results[0]
        return {'gene_id': genomic_feature.name,
                'chromosome_id': genomic_feature.chr,
                'genomic_feature': genomic_feature}


class GetGenomicFeatureByInterval(Action):
        
    IN = ['genomic_feature_set', 'genomic_interval']
    OUT = ['genomic_feature']

    def calculate(self, genomic_feature_set, genomic_interval):
        #TODO: select correct gene
        gene_model = genomic_feature_set.fetch(
            genomic_interval['chromosome_id'],
            genomic_interval['start'],
            genomic_interval['stop'])
        if gene_model is None or len(gene_model) == 0:
            return None
        gene = gene_model[0]
        return {'gene_id': gene.name, 'chromosome_id': gene.chr, 'genomic_feature': gene}
