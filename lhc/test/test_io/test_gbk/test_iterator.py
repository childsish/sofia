__author__ = 'Liam Childs'

import unittest

from lhc.io.gbk import GbkIterator


class TestIterator(unittest.TestCase):
    def setUp(self):
        self.lines = """LOCUS       U00096               4641652 bp    DNA     circular BCT 01-AUG-2014
DEFINITION  Escherichia coli str. K-12 substr. MG1655, complete genome.
ACCESSION   U00096
VERSION     U00096.3  GI:545778205
DBLINK      BioProject: PRJNA225
            BioSample: SAMN02604091
KEYWORDS    .
SOURCE      Escherichia coli str. K-12 substr. MG1655
  ORGANISM  Escherichia coli str. K-12 substr. MG1655
            Bacteria; Proteobacteria; Gammaproteobacteria; Enterobacteriales;
            Enterobacteriaceae; Escherichia.
REFERENCE   1  (bases 1 to 4641652)
  AUTHORS   Blattner,F.R., Plunkett,G. III, Bloch,C.A., Perna,N.T., Burland,V.,
            Riley,M., Collado-Vides,J., Glasner,J.D., Rode,C.K., Mayhew,G.F.,
            Gregor,J., Davis,N.W., Kirkpatrick,H.A., Goeden,M.A., Rose,D.J.,
            Mau,B. and Shao,Y.
  TITLE     The complete genome sequence of Escherichia coli K-12
  JOURNAL   Science 277 (5331), 1453-1462 (1997)
   PUBMED   9278503
REFERENCE   2  (bases 1 to 4641652)
  AUTHORS   Hayashi,K., Morooka,N., Yamamoto,Y., Fujita,K., Isono,K., Choi,S.,
            Ohtsubo,E., Baba,T., Wanner,B.L., Mori,H. and Horiuchi,T.
  TITLE     Highly accurate genome sequences of Escherichia coli K-12 strains
            MG1655 and W3110
  JOURNAL   Mol. Syst. Biol. 2, 2006 (2006)
   PUBMED   16738553
REFERENCE   3  (bases 1 to 4641652)
  AUTHORS   Riley,M., Abe,T., Arnaud,M.B., Berlyn,M.K., Blattner,F.R.,
            Chaudhuri,R.R., Glasner,J.D., Horiuchi,T., Keseler,I.M., Kosuge,T.,
            Mori,H., Perna,N.T., Plunkett,G. III, Rudd,K.E., Serres,M.H.,
            Thomas,G.H., Thomson,N.R., Wishart,D. and Wanner,B.L.
  TITLE     Escherichia coli K-12: a cooperatively developed annotation
            snapshot--2005
  JOURNAL   Nucleic Acids Res. 34 (1), 1-9 (2006)
   PUBMED   16397293
  REMARK    Publication Status: Online-Only
FEATURES             Location/Qualifiers
     source          1..4641652
                     /organism="Escherichia coli str. K-12 substr. MG1655"
                     /mol_type="genomic DNA"
                     /strain="K-12"
                     /sub_strain="MG1655"
                     /db_xref="taxon:511145"
     gene            190..255
                     /gene="thrL"
                     /locus_tag="b0001"
                     /gene_synonym="ECK0001"
                     /gene_synonym="JW4367"
                     /db_xref="EcoGene:EG11277"
     CDS             190..255
                     /gene="thrL"
                     /locus_tag="b0001"
                     /gene_synonym="ECK0001"
                     /gene_synonym="JW4367"
                     /function="leader; Amino acid biosynthesis: Threonine"
                     /note="GO_process: GO:0009088 - threonine biosynthetic
                     process"
                     /codon_start=1
                     /transl_table=11
                     /product="thr operon leader peptide"
                     /protein_id="AAC73112.1"
                     /db_xref="GI:1786182"
                     /db_xref="ASAP:ABE-0000006"
                     /db_xref="UniProtKB/Swiss-Prot:P0AD86"
                     /db_xref="EcoGene:EG11277"
                     /translation="MKRISTTITTTITITTGNGAG"
     gene            58474..59279
                     /gene="yabP"
                     /locus_tag="b4659"
                     /gene_synonym="ECK0057"
                     /gene_synonym="JW0055"
                     /gene_synonym="yabQ"
                     /pseudo
                     /db_xref="EcoGene:EG12610"
     CDS             join(58474..59052,59052..59279)
                     /gene="yabP"
                     /locus_tag="b4659"
                     /gene_synonym="ECK0057"
                     /gene_synonym="JW0055"
                     /gene_synonym="yabQ"
                     /note="pseudogene, pentapeptide repeats-containing"
                     /pseudo
                     /codon_start=1
                     /transl_table=11
                     /db_xref="ASAP:ABE-0000192"
                     /db_xref="ASAP:ABE-0000194"
                     /db_xref="UniProtKB/Swiss-Prot:P39220"
                     /db_xref="EcoGene:EG12610"
     gene            complement(59687..60346)
                     /gene="rluA"
                     /locus_tag="b0058"
                     /gene_synonym="ECK0059"
                     /gene_synonym="JW0057"
                     /gene_synonym="yabO"
                     /db_xref="EcoGene:EG12609"
     CDS             complement(59687..60346)
                     /gene="rluA"
                     /locus_tag="b0058"
                     /gene_synonym="ECK0059"
                     /gene_synonym="JW0057"
                     /gene_synonym="yabO"
                     /EC_number="4.2.1.70"
                     /function="enzyme; rRNA modification; tRNA modification"
                     /note="GO_process: GO:0009451 - RNA modification"
                     /codon_start=1
                     /transl_table=11
                     /product="dual specificity 23S rRNA pseudouridine(746),
                     tRNA pseudouridine(32) synthase, SAM-dependent"
                     /protein_id="AAC73169.1"
                     /db_xref="GI:1786244"
                     /db_xref="ASAP:ABE-0000196"
                     /db_xref="UniProtKB/Swiss-Prot:P0AA37"
                     /db_xref="EcoGene:EG12609"
                     /translation="MGMENYNPPQEPWLVILYQDDHIMVVNKPSGLLSVPGRLEEHKD
                     SVMTRIQRDYPQAESVHRLDMATSGVIVVALTKAAERELKRQFREREPKKQYVARVWG
                     HPSPAEGLVDLPLICDWPNRPKQKVCYETGKPAQTEYEVVEYAADNTARVVLKPITGR
                     SHQLRVHMLALGHPILGDRFYASPEARAMAPRLLLHAEMLTITHPAYGNSMTFKAPAD
                     F"

ORIGIN
        1 agcttttcat tctgactgca acgggcaata tgtctctgtg tggattaaaa aaagagtgtc
       61 tgatagcagc ttctgaactg gttacctgcc gtgagtaaat taaaatttta ttgacttagg
      121 tcactaaata ctttaaccaa tataggcata gcgcacagac agataaaaat tacagagtac
      181 acaacatcca tgaaacgcat tagcaccacc attaccacca ccatcaccat taccacaggt
      241 aacggtgcgg gctgacgcgt acaggaaaca cagaaaaaag cccgcacctg acagtgcggg
      301 cttttttttt cgaccaaagg taacgaggta acaaccatgc gagtgttgaa gttcggcggt
      361 acatcagtgg caaatgcaga acgttttctg cgtgttgccg atattctgga aagcaatgcc
      421 aggcaggggc aggtggccac cgtcctctct gcccccgcca aaatcaccaa ccacctggtg
      481 gcgatgattg aaaaaaccat tagcggccag gatgctttac ccaatatcag cgatgccgaa
      541 cgtatttttg ccgaactttt gacgggactc gccgccgccc agccggggtt cccgctggcg
      601 caattgaaaa ctttcgtcga tcaggaattt gcccaaataa aacatgtcct gcatggcatt
      661 agtttgttgg ggcagtgccc ggatagcatc aacgctgcgc tgatttgccg tggcgagaaa
      721 atgtcgatcg ccattatggc cggcgtatta gaagcgcgcg gtcacaacgt tactgttatc
      781 gatccggtcg aaaaactgct ggcagtgggg cattacctcg aatctaccgt cgatattgct
      841 gagtccaccc gccgtattgc ggcaagccgc attccggctg atcacatggt gctgatggca
      901 ggtttcaccg ccggtaatga aaaaggcgaa ctggtggtgc ttggacgcaa cggttccgac
      961 tactctgctg cggtgctggc tgcctgttta cgcgccgatt gttgcgagat ttggacggac

""".split('\n')

    def test_init(self):
        it = GbkIterator(self.lines)

        self.assertIn('LOCUS', it.hdr)
        self.assertEquals('U00096               4641652 bp    DNA     circular BCT 01-AUG-2014',
                          it.hdr['LOCUS']['value'])
        self.assertIn('DEFINITION', it.hdr)
        self.assertIn('ACCESSION', it.hdr)
        self.assertIn('VERSION', it.hdr)
        self.assertIn('DBLINK', it.hdr)
        self.assertEquals('BioProject: PRJNA225 BioSample: SAMN02604091', it.hdr['DBLINK']['value'])
        self.assertIn('KEYWORDS', it.hdr)
        self.assertIn('SOURCE', it.hdr)
        self.assertEquals('Escherichia coli str. K-12 substr. MG1655', it.hdr['SOURCE']['value'])
        self.assertEquals('Escherichia coli str. K-12 substr. MG1655 Bacteria; Proteobacteria; Gammaproteobacteria; Enterobacteriales; Enterobacteriaceae; Escherichia.', it.hdr['SOURCE']['ORGANISM']['value'])
        self.assertIn('REFERENCE', it.hdr)
        self.assertEquals(3, len(it.hdr['REFERENCE']))
        self.assertEquals('1  (bases 1 to 4641652)', it.hdr['REFERENCE'][0]['value'])
        self.assertEquals('The complete genome sequence of Escherichia coli K-12', it.hdr['REFERENCE'][0]['TITLE']['value'])
        self.assertEquals('9278503', it.hdr['REFERENCE'][0]['JOURNAL']['PUBMED']['value'])

    def test_next(self):
        it = GbkIterator(self.lines)

        n = it.next()
        self.assertEquals(0, n.start)
        self.assertEquals(4641652, n.stop)
        self.assertEquals('source', n.type)
        self.assertEquals('Escherichia coli str. K-12 substr. MG1655', n.data['organism'])

        n = it.next()
        self.assertEquals('gene', n.type)
        self.assertEquals(189, n.start)
        self.assertEquals(255, n.stop)
        n = it.next()
        self.assertEquals('CDS', n.type)
        self.assertEquals(189, n.start)
        self.assertEquals(255, n.stop)
        self.assertEquals(0, n.data['codon_start'])
        self.assertEquals(11, n.data['transl_table'])

if __name__ == '__main__':
    unittest.main()
