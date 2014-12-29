import os
import tempfile
import unittest

from ebias.entity_graph import EntityGraph


class TestEntityGraph(unittest.TestCase):
    def setUp(self):
        fhndl, fname = tempfile.mkstemp()
        os.write(fhndl, """{
    "variant": ["genomic_position", "ref", "alt*", "qual", "sample*"],
    "genomic_position": ["chromosome_id", "chromosome_pos"],
    "sample": ["GT", "GQ", "RO", "AO*"],
    "gene_model": ["gene_id", "chromosome_id", "transcript*"],
    "transcript": ["exon*"],
    "exon": ["exon_start", "exon_stop"]
}
""")
        os.close(fhndl)
        self.graph = EntityGraph(fname)

    def test_get_ancestor_paths(self):
        paths = self.graph.getAncestorPaths('chromosome_pos')
        self.assertEquals(len(paths), 2)
        self.assertEquals(paths[0], ['genomic_position', 'chromosome_pos'])
        self.assertEquals(paths[1], ['variant', 'genomic_position', 'chromosome_pos'])

    def test_get_descendents_paths(self):
        paths = sorted(self.graph.getDescendentPaths('variant'))
        self.assertEquals(len(paths), 7)
        self.assertEquals(paths[0], ['variant', 'alt*'])
        self.assertEquals(paths[1], ['variant', 'genomic_position'])
        self.assertEquals(paths[2], ['variant', 'genomic_position', 'chromosome_id'])
        self.assertEquals(paths[3], ['variant', 'genomic_position', 'chromosome_pos'])
        self.assertEquals(paths[4], ['variant', 'qual'])
        self.assertEquals(paths[5], ['variant', 'ref'])
        self.assertEquals(paths[6], ['variant', 'sample*'])

if __name__ == "__main__":
    unittest.main()
