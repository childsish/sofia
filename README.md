lhc-python
==========

This is my personal library of python classes and functions, many of them have bioinformatics applications. The library changes constantly and at a whim. If you want to use it, approach with caution. Over time however, parts appear to be settling on a stable configuration.

binf
----
A collection of bioinformatics related modules

### binf.collection
Several collection classes that to handle biological data. They are designed to read from files that have strict standards and provide some access benefits eg. NetCDF and SQLite.

* **binf.collection.marker_set.** A class designed to hold marker data. Implemented as NetCDF4. Markers are considered a genomic position that varies across several genotypes, thus is implemented as a matrix of genotype x genomic position.

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