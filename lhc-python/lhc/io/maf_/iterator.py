import bz2
import gzip

from collections import namedtuple

MafLine = namedtuple('MafLine', ('hugo_symbol', 'entrez_gene_id', 'center', 'ncbi_build', 'chromosome', 'start_position',
                                 'end_position', 'strand', 'variant_classification', 'variant_type', 'reference_allele',
                                 'tumour_seq_allele1', 'tumour_seq_allele2', 'dnsnp_rs', 'dbsnp_val_status',
                                 'tumour_sample_barcode', 'matched_norm_sample_barcode', 'match_norm_seq_allele1',
                                 'match_norm_seq_allele2', 'tumour_validation_allele1', 'tumour_validation_allele2',
                                 'match_norm_validation_allele1', 'match_norm_validation_allele2',
                                 'verification_status', 'validation_status', 'mutation_status', 'sequencing_phase',
                                 'sequence_source', 'validation_method', 'score', 'bam_file', 'sequencer',
                                 'tumour_sample_uuid', 'matched_norm_sample_uuid', 'cosmic_codon', 'cosmic_gene',
                                 'transcript_id', 'exon', 'chrom_change', 'aa_change', 'genome_plus_minus_10_bp',
                                 'drug_target', 'ttot_cov', 'tvar_cov', 'ntot_cov', 'nvar_cov', 'dbSNPPopFreq'))


class MafIterator(object):
    def __init__(self, fname):
        self.line_no = 0
        self.fname = fname
        self.fhndl =\
            gzip.open(fname) if fname.endswith('.gz') else\
            bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            open(fname)

    def __iter__(self):
        return self

    def next(self):
        line = self.fhndl.readline()
        if line == '':
            raise StopIteration()
        self.line_no += 1
        return MafLine(*line.rstrip('\r\n').split('\t'))
