Sequence Features
=================
These modules calculate various sequence features.

Each module can be used individually simply by calling the Feature.calculate(sequence) function with the sequence you want to calculate the feature for. To reduce redundant calculations I also started implementing a system where dependencies can be specified. This system uses the Feature.generate function.

Codon features
--------------

### The effective number of codons
http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1456227/
A method for measuring the synonymous codon usage bias.
