from functools import partial
from table import iterTable

iterGff = partial(iterTable, typ='gff')
