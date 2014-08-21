from itertools import chain
from ebias.feature import Feature

class GeneName(Feature):
    
    IN = ['gene_model']
    OUT = ['gene_name']
    
    def calculate(self, gene_model):
        if gene_model is None:
            return ''
        return {model.name: model.name for model in gene_model.itervalues()}\
            if isinstance(gene_model, dict)\
            else gene_model.name
    
    def format(self, gene_name):
        return ','.join(gene_name) if isinstance(gene_name, dict) else gene_name

class GenePosition(Feature):
    
    IN = ['genomic_position', 'gene_model']
    OUT = ['gene_position']

    def calculate(self, genomic_position, gene_model):
        transcripts = chain.from_iterable(model.transcripts.itervalues()\
                for model in gene_model.itervalues())\
            if isinstance(gene_model, dict)\
            else gene_model.transcripts.itervalues()
        return {t.name: t.getRelPos(genomic_position.pos) for t in transcripts\
            if t is not None}

    def format(self, gene_position):
        return ','.join('%s:%d'%(k, v + 1) for k, v in gene_position)\
            if isinstance(gene_position, dict)\
            else str(gene_position + 1)

