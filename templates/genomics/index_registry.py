from lhc.indices import KeyIndex, IntervalIndex, CompoundIndex

INDEX_REGISTRY = {
    'gr': lambda: CompoundIndex(KeyIndex, IntervalIndex, key=lambda gr: (gr.chr, gr))
}
