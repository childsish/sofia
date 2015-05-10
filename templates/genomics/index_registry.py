from lhc.indices import KeyIndex, IntervalIndex, CompoundIndex

INDEX_REGISTRY = {
    'k': KeyIndex,
    'v': IntervalIndex,
    'gv': lambda: CompoundIndex(KeyIndex, IntervalIndex, key=lambda gv: (gv.chr, gv))
}
