from sofia_.step import Step


class GetGenomicFeatureByPosition(Step):
    
    IN = ['genomic_feature_set', 'genomic_position']
    OUT = ['genomic_feature']

    def calculate(self, genomic_feature_set, genomic_position):
        if genomic_position is None:
            return None
        #TODO: select correct gene (currently selecting largest)
        features = genomic_feature_set.fetch(
            genomic_position.chr,
            genomic_position.pos,
            genomic_position.pos + 1)
        if features is None or len(features) == 0:
            return None
        res = sorted(features, key=len)[-1]
        res.name = res.name.rsplit('.')[0]
        return res


class GetGenomicFeatureByInterval(Step):
        
    IN = ['genomic_feature_set', 'genomic_interval']
    OUT = ['genomic_feature']

    def calculate(self, genomic_feature_set, genomic_interval):
        #TODO: select correct gene (currently selecting largest)
        features = genomic_feature_set.fetch(
            genomic_interval.chr,
            genomic_interval.start,
            genomic_interval.stop)
        if features is None or len(features) == 0:
            return None
        res = sorted(features, key=len)[-1]
        res.name = res.name.rsplit('.')[0]
        return res
