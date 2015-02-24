RAW = """A	Ala	Alanine
C	Cys	Cysteine
D	Asp	Aspartic Acid
E	Glu	Glutamic Acid
F	Phe	Phenylalanine
G	Gly	Glycine
H	His	Histidine
I	Ile	Isoleucine
K	Lys	Lysine
L	Leu	Leucine
M	Met	Methionine
N	Asn	Asparagine
P	Pro	Proline
Q	Gln	Glutamine
R	Arg	Arginine
S	Ser	Serine
T	Thr	Threonine
V	Val	Valine
W	Trp	Tryptophan
Y	Tyr	Tyrosine
*	*	Stop"""

DATA = [line.split('\t') for line in RAW.split('\n')]

AA_MAP = {}
for i, parts in enumerate(DATA):
    for part in parts:
        AA_MAP[part] = i

def get_one_code(key):
    return DATA[AA_MAP[key]][0]

def get_three_code(key):
    return DATA[AA_MAP[key]][1]

def get_full_name(key):
    return DATA[AA_MAP[key]][2]
