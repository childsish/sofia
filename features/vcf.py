from ebias.feature import Feature

class AccessVcfByPosition(Feature):
    
    IN = ['vcf', 'genomic_position']
    OUT = ['variant', 'genomic_position']

    def calculate(self, vcf, genomic_position):
        return vcf[genomic_position]

class AccessVcfByInterval(Feature):
    
    IN = ['vcf', 'genomic_interval']
    OUT = ['variant', 'genomic_position']
    
    def calculate(self, vcf, genomic_interval):
        return vcf[genomic_interval]

class AccessVcfByGeneModel(Feature):
    
    IN = ['vcf', 'gene_model']
    OUT = ['variant', 'genomic_position']
    
    def calculate(self, vcf, gene_model):
        return vcf[gene_model.ivl]

class MatchVcf(Feature):
    
    IN = ['variant']
    OUT = ['vcf_match']
    
    def calculate(self, variant):
        return variant is not None

class VariantSampleCount(Feature):
    
    IN = ['variant']
    OUT = ['variant_sample_count']
    
    def calculate(self, variant):
        return sum(v['GT'] != '0/0' for v in variant.samples.itervalues())

class VariantCount(Feature):
    
    IN = ['variant']
    OUT = ['variant_count']
    
    def calculate(self, variant):
        return len(variant)
