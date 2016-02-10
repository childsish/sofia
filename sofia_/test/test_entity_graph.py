import os
import unittest

from sofia_.graph.entity_graph import EntityGraph


class TestEntityGraph(unittest.TestCase):
    def setUp(self):
        fname = os.path.join(__file__[:__file__.index('sofia_')], 'templates', 'genomics', 'entities.json')
        self.graph = EntityGraph(fname)

    def test_get_descendents_paths(self):
        paths = sorted(self.graph.get_descendent_paths('variant'))
        paths = {path[-1]['name']: path for path in paths}
        self.assertEquals(len(paths), 5)
        self.assertEquals([{'type': 'attr', 'name': 'chromosome_id', 'key': 'chr'}], paths['chromosome_id'])
        self.assertEquals([{'type': 'attr', 'name': 'chromosome_pos', 'key': 'pos'}], paths['chromosome_pos'])
        self.assertEquals([{'type': 'attr', 'name': 'reference_allele', 'key': 'ref'}], paths['reference_allele'])
        self.assertEquals([{'type': 'attr', 'name': 'alternate_allele', 'key': 'alt'}], paths['alternate_allele'])
        self.assertEquals([{'type': 'attr', 'name': 'variant_quality', 'key': 'qual'}], paths['variant_quality'])

if __name__ == "__main__":
    unittest.main()
