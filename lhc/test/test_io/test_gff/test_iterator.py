import unittest

from StringIO import StringIO
from lhc.io.gff_.iterator import GffEntryIterator


class TestGffIterator(unittest.TestCase):
    def test_iterator(self):
        fhndl = StringIO(file_content)
        it = GffEntryIterator(fhndl)

        self.assertEquals('AT1G01010', it.next().name)
        self.assertEquals('AT1G01020', it.next().name)
        self.assertRaises(StopIteration, it.next)

file_content = """Chr1	TAIR10	chromosome	1	30427671	.	.	.	ID=Chr1;Name=Chr1
Chr1	TAIR10	gene	3631	5899	.	+	.	ID=AT1G01010;Note=protein_coding_gene;Name=AT1G01010
Chr1	TAIR10	mRNA	3631	5899	.	+	.	ID=AT1G01010.1;Parent=AT1G01010;Name=AT1G01010.1;Index=1
Chr1	TAIR10	protein	3760	5630	.	+	.	ID=AT1G01010.1-Protein;Name=AT1G01010.1;Derives_from=AT1G01010.1
Chr1	TAIR10	exon	3631	3913	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	five_prime_UTR	3631	3759	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	CDS	3760	3913	.	+	0	Parent=AT1G01010.1,AT1G01010.1-Protein;
Chr1	TAIR10	exon	3996	4276	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	CDS	3996	4276	.	+	2	Parent=AT1G01010.1,AT1G01010.1-Protein;
Chr1	TAIR10	exon	4486	4605	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	CDS	4486	4605	.	+	0	Parent=AT1G01010.1,AT1G01010.1-Protein;
Chr1	TAIR10	exon	4706	5095	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	CDS	4706	5095	.	+	0	Parent=AT1G01010.1,AT1G01010.1-Protein;
Chr1	TAIR10	exon	5174	5326	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	CDS	5174	5326	.	+	0	Parent=AT1G01010.1,AT1G01010.1-Protein;
Chr1	TAIR10	exon	5439	5899	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	CDS	5439	5630	.	+	0	Parent=AT1G01010.1,AT1G01010.1-Protein;
Chr1	TAIR10	three_prime_UTR	5631	5899	.	+	.	Parent=AT1G01010.1
Chr1	TAIR10	gene	5928	8737	.	-	.	ID=AT1G01020;Note=protein_coding_gene;Name=AT1G01020
Chr1	TAIR10	mRNA	5928	8737	.	-	.	ID=AT1G01020.1;Parent=AT1G01020;Name=AT1G01020.1;Index=1
Chr1	TAIR10	protein	6915	8666	.	-	.	ID=AT1G01020.1-Protein;Name=AT1G01020.1;Derives_from=AT1G01020.1
Chr1	TAIR10	five_prime_UTR	8667	8737	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	8571	8666	.	-	0	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	8571	8737	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	8417	8464	.	-	0	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	8417	8464	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	8236	8325	.	-	0	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	8236	8325	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	7942	7987	.	-	0	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	7942	7987	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	7762	7835	.	-	2	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	7762	7835	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	7564	7649	.	-	0	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	7564	7649	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	7384	7450	.	-	1	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	7384	7450	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	7157	7232	.	-	0	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	exon	7157	7232	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	CDS	6915	7069	.	-	2	Parent=AT1G01020.1,AT1G01020.1-Protein;
Chr1	TAIR10	three_prime_UTR	6437	6914	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	exon	6437	7069	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	three_prime_UTR	5928	6263	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	exon	5928	6263	.	-	.	Parent=AT1G01020.1
Chr1	TAIR10	mRNA	6790	8737	.	-	.	ID=AT1G01020.2;Parent=AT1G01020;Name=AT1G01020.2;Index=1
Chr1	TAIR10	protein	7315	8666	.	-	.	ID=AT1G01020.2-Protein;Name=AT1G01020.2;Derives_from=AT1G01020.2
Chr1	TAIR10	five_prime_UTR	8667	8737	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	8571	8666	.	-	0	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	exon	8571	8737	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	8417	8464	.	-	0	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	exon	8417	8464	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	8236	8325	.	-	0	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	exon	8236	8325	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	7942	7987	.	-	0	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	exon	7942	7987	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	7762	7835	.	-	2	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	exon	7762	7835	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	7564	7649	.	-	0	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	exon	7564	7649	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	CDS	7315	7450	.	-	1	Parent=AT1G01020.2,AT1G01020.2-Protein;
Chr1	TAIR10	three_prime_UTR	7157	7314	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	exon	7157	7450	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	three_prime_UTR	6790	7069	.	-	.	Parent=AT1G01020.2
Chr1	TAIR10	exon	6790	7069	.	-	.	Parent=AT1G01020.2"""

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())