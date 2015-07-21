from lhc.binf.genomic_coordinate import GenomicInterval
from lhc.io.vcf_.iterator import Variant

ENTITY_REGISTRY = {
    'gr': GenomicInterval,
    'v': Variant
}
