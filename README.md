ebias
=====

Extensible BioInformation Aggregation System

example command:

> python -m run_ebias D:\data\tmp.vcf Chromosome Position GeneName AminoAcidVariant VariantType -r D:\data\tmp.gtf D:\data\tmp.fasta

Creating a new feature
----------------------
New features are implemented by creating a new Python class that inherits from the Feature class found in modules.feature. A feature consists of several concepts.
1. **The name of the feature.** This is the name that is referred to from the command line and other features. It is defined by the class variable "NAME".
2. **Resources used.** A list of the resource names that the feature will use. These names are specified by the user on the command line. Resources are defined by the class variable "RESOURCES".
3. **Dependencies on other features.** A list of the other features or resources that this feature depends on. Each dependent feature is defined by three key:value pairs. The name of the dependent feature is defined by the key "name", the class by the key "feature" and the how the resources used by the current feature are mapped to the dependent feature by the key "resource_map". Dependencies are defined by the class variable "DEPENDENCIES".
4. **Calculating the feature.** The function to actually calculate the desired feature also needs to be defined. The arguments that are passed to it are determined by the names of the given dependencies. The function is defined by the class member "calculate".
5. **Formatting the results (optional).** The output of "calculate" can be formatted before the final output by the "format" function.

Design Philosophy
-----------------

Batteries included.

 * There should be as few library dependencies as possible.

The user has to change the resource data as little as possible.

 * This means that gzipped files can not be indexed as gzip indexing requires the file to be unzipped and re-zipped using tabix. Using tabix would also require an extra library

The tool should be easily extended.

 * The default state is not a one-size-fits-all solution. Different groups have different needs. However, it should be easily extended to accomodate new types of resources and features.
 * As much adaptation as possible should be carried out on the command line.


Other considerations
--------------------

It is not intended to be a workflow engine.

It should be able to annotate any set of bioloical entities.

Give the resource types with initialisation?

-t name:TableResource:


Multiple VCFs
-------------

-r name:dname -t name:multivcf

To Do
-----

To Test
-------

VCF <=> GTF
GTF <=> VCF
