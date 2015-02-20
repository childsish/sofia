import os
import tempfile
import unittest

from lhc.io.txt_.index import IndexedFile
from lhc.io.txt_.compress import compress


class TestIndexedFile(unittest.TestCase):
    def test_fetch_point(self):
        content = """Chr1	TAIR10	gene	3631	5899	.	+	.	ID=AT1G01010;Note=protein_coding_gene;Name=AT1G01010
Chr1	TAIR10	mRNA	3631	5899	.	+	.	ID=AT1G01010.1;Parent=AT1G01010;Name=AT1G01010.1;Index=1
Chr1	TAIR10	gene	5928	8737	.	-	.	ID=AT1G01020;Note=protein_coding_gene;Name=AT1G01020
Chr1	TAIR10	mRNA	5928	8737	.	-	.	ID=AT1G01020.1;Parent=AT1G01020;Name=AT1G01020.1;Index=1
Chr1	TAIR10	mRNA	6790	8737	.	-	.	ID=AT1G01020.2;Parent=AT1G01020;Name=AT1G01020.2;Index=1
Chr2	TAIR10	gene	3706	5513	.	+	.	ID=AT2G01010;Note=rRNA;Name=AT2G01010
Chr2	TAIR10	rRNA	3706	5513	.	+	.	ID=AT2G01010.1;Parent=AT2G01010;Name=AT2G01010.1;Index=1
Chr2	TAIR10	exon	3706	5513	.	+	.	Parent=AT2G01010.1
Chr2	TAIR10	gene	5782	5945	.	+	.	ID=AT2G01020;Note=rRNA;Name=AT2G01020
Chr2	TAIR10	rRNA	5782	5945	.	+	.	ID=AT2G01020.1;Parent=AT2G01020;Name=AT2G01020.1;Index=1
Chr2	TAIR10	exon	5782	5945	.	+	.	Parent=AT2G01020.1"""
        fhndl, fname = tempfile.mkstemp()
        os.write(fhndl, content)
        os.close(fhndl)
        compress(fname, ['1s', '4.5v'])

        index = IndexedFile('{}.bgz'.format(fname))

        content = [line + '\n' for line in content.split('\n') if line.strip() != '']
        lines = index.fetch('Chr1', 4000)
        self.assertEquals(content[:2], lines)
        lines = index.fetch('Chr1', 7000)
        self.assertEquals(content[2:5], lines)
        lines = index.fetch('Chr2', 5000)
        self.assertEquals(content[5:8], lines)

    def test_fetch_interval(self):
        content = """Chr1	TAIR10	gene	3631	5899	.	+	.	ID=AT1G01010;Note=protein_coding_gene;Name=AT1G01010
Chr1	TAIR10	mRNA	3631	5899	.	+	.	ID=AT1G01010.1;Parent=AT1G01010;Name=AT1G01010.1;Index=1
Chr1	TAIR10	gene	5928	8737	.	-	.	ID=AT1G01020;Note=protein_coding_gene;Name=AT1G01020
Chr1	TAIR10	mRNA	5928	8737	.	-	.	ID=AT1G01020.1;Parent=AT1G01020;Name=AT1G01020.1;Index=1
Chr1	TAIR10	mRNA	6790	8737	.	-	.	ID=AT1G01020.2;Parent=AT1G01020;Name=AT1G01020.2;Index=1
Chr2	TAIR10	gene	3706	5513	.	+	.	ID=AT2G01010;Note=rRNA;Name=AT2G01010
Chr2	TAIR10	rRNA	3706	5513	.	+	.	ID=AT2G01010.1;Parent=AT2G01010;Name=AT2G01010.1;Index=1
Chr2	TAIR10	exon	3706	5513	.	+	.	Parent=AT2G01010.1
Chr2	TAIR10	gene	5782	5945	.	+	.	ID=AT2G01020;Note=rRNA;Name=AT2G01020
Chr2	TAIR10	rRNA	5782	5945	.	+	.	ID=AT2G01020.1;Parent=AT2G01020;Name=AT2G01020.1;Index=1
Chr2	TAIR10	exon	5782	5945	.	+	.	Parent=AT2G01020.1
"""
        fhndl, fname = tempfile.mkstemp()
        os.write(fhndl, content)
        os.close(fhndl)
        compress(fname, ['1s', '4.5v'])

        index = IndexedFile('{}.bgz'.format(fname))

        content = [line + '\n' for line in content.split('\n') if line.strip() != '']
        lines = index.fetch('Chr1', 4000, 8000)
        self.assertEquals(content[:5], lines)
        lines = index.fetch('Chr2', 5800, 8000)
        self.assertEquals(content[8:], lines)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
