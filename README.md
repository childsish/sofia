SoFIA
=====

Software for the Flexible Integration of Annotation (SoFIA) is a framework designed to make integrating information from multiple sources as easy and painless as possible. This is achieved through the use of a worflow engine capable of automatic workflow resolution. In practice, this means that the user only needs to provide the resources they wish to draw their information from and the entities they wish to calculate from the resources, and the framework will do the rest.

By default, vanilla SoFIA comes with a workflow that can annotate variants and genes, and can also calculate sequence features. If different functionality is required, SoFIA has been designed to be extensible allowing the user to easily extend the current workflow or even create a whole new workflow for completely different purposes.

Installation
------------

### Dependencies

SoFIA requires [Python 2.7][python] to be installed.

The framework of SoFIA has no dependencies on external libraries. However, the default workflow has 'soft' dependencies on the [htslib][htslib] and [pysam][pysam] libraries for indexing various file formats. If either of these libraries is not installed, then the framework will resort to reading in the entire file. This can significantly slow down the framework.

### via Source

As a Python program, SoFIA does not need to be compiled. As such, you can simply download the source and run it. However, You will need to check for updates.

1. Download and unzip the compressed version from GitHub:
https://github.com/childsish/sofia/releases/latest
2. Extract the file to desired installation directory
3. (optional) Add the installation directory to the PATH environment variable.

### via Git

1. Change to desired installation directory
2. To install `git clone git@github.com:childsish/sofia.git`
3. (optional) Add the installation directory to the PATH environment variable.
4. To update: `git pull`

`sofia D:\data\tmp.vcf Chromosome Position GeneName AminoAcidVariant VariantType -r D:\data\tmp.gtf D:\data\tmp.fasta`

Creating a new action
---------------------

New actions are implemented by creating a new Python class that inherits from the action class found in modules.action. A action consists of several concepts.

1. **The name of the action.** This is the name that is referred to from the command line and other actions. It is defined by the name of the class.
2. **Required entities.** A list of entities that the action will use. Required entities are defined by the class variable "IN".
3. **Provided entities.** A list of entities that the action will provide. Provided entities are defined by the class variable "OUT".
4. **Calculating the action.** The function to actually calculate the desired action also needs to be defined. The arguments that are passed to it are determined by the names of the given dependencies. The function is defined by the class member "calculate".
5. **Formatting the results (optional).** The output of "calculate" can be formatted before the final output by the "format" function.

Design Philosophy
-----------------

Batteries included.

 * There should be as few library dependencies as possible.

The user has to change the resource data as little as possible.
 
 * Ideally, all files can be used as-is. However, indexing the file is highly recommended as it will greatly speed up the framework. Indexing using the [htslib][htslib] is supported by default.

The tool should be easily extended.

 * The default state is not a one-size-fits-all solution. Different groups have different needs. However, it should be easily extended to accomodate new types of resources and actions.


Standardisation (Variant annotation)
------------------------------------

The variant annotation workflow that comes with SoFIA attempts to follow the guidelines laid out by the [Human Genome Variation Society][hgvs] when showing the coding and amino acid changes. However, we deviate from the guidelines by using only the 1-letter code for amino acids. Any other deviation is unintentional and should be brought to my attention.

The variant annotation workflow also attempts to follow the [The Sequence Ontology][so] when describing the type of variant. Any deviation is unintentional and should be brought to my attention.


To Do
-----

There are still many ways in which SoFIA can be improved. Here are some that I plan to do, but I am always open to suggestions.

* Incorporate programs that work on whole sets.

[python]: https://www.python.org/downloads/ "Download Python 2.7"
[htslib]: http://www.htslib.org/ "Download htslib"
[pysam]: https://code.google.com/p/pysam/ "Download pysam"
[hgvs]: http://www.hgvs.org/mutnomen/ "Human Genome Variation Society"
[so]: http://www.sequenceontology.org/ "The Sequence Ontology"
