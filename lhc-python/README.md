lhc-python
==========

This is my personal library of python classes and functions, many of them have bioinformatics applications. The library changes constantly and at a whim. If you want to use it, approach with caution. Over time however, parts appear to be settling on a stable configuration.

binf
----
A collection of bioinformatics related modules

### binf.collection
Several collection classes that to handle biological data. They are designed to read from files that have strict standards and provide some access benefits eg. NetCDF and SQLite.

* **binf.collection.marker_set.** A class designed to hold marker data. Implemented as NetCDF4. Markers are considered a genomic position that varies across several genotypes, thus is implemented as a matrix of genotype x genomic position.

There are a couple of steps required to initialise this class. You need to provide a reference sequence and the positions of the reference sequence. The reference sequence is a n x m matrix where n is the position and m is the ploidy. The positions are provided as an ordered dictionary of chromosomes to a list of positions.
```python
from lhc.binf.collection.marker_set import Reference, MarkerSet
mrks = 'ACGATCAGGCT'
ref = Reference(ref=np.vstack([list(mrks), list(mrks)]).T,
    poss=OrderedDict([
        ('Chr1', [5, 10, 15, 20, 25]),
        ('Chr2', [4, 6, 8, 10, 12, 14])
    ]))
mrk_set = MarkerSet(self.fname, ref)
```
For each genotype you call the registerGenotype function with the name of the genotype and the markers.
```python
mrks = 'ACGACTGGGCT'
mrk_set.registerGenotype('genotype_A',
    np.vstack([list(mrks), list(mrks)]).T)
```
You can now use the functions getMarkerAtPosition and getMarkersInInterval to retrieve the desired markers. You can also use getGenotype to get all the markers for a particular genotype.

You can register alternative names for a genotype by passing the main_name argument to the registerGenotype function.

* **binf.collection.model_set.** A class designed to hold gene models. Implemented as SQLite with R*tree support to enable fast interval queries.

* **binf.collection.sequence_set.** A class designed to hold several sequences (probably belonging to a single species). Implemented as NetCDF4. Provides fast access to sequences.

* **binf.collection.variant_set.** A class designed to hold the variant positions for a single genotype/sample. Will be re-implemented as SQLite.

collection
----------
Several collections mostly to do with intervals

file_format
-----------
Parsers for several file formats

stats
-----
Some experimental stats modules mostly to do with cumulative stats

test
----
Unit tests. Completely out-of-date...
