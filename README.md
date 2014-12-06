SoFIA
=====

Extensible BioInformation Aggregation System

Installation
------------

### Windows

1. Download and unzip the compressed version from GitHub:
https://github.com/childsish/sofia/archive/master.zip
2. Extract the file to desired directory
3. Add the directory to the environment variable PYTHONPATH

> python -m run_sofia D:\data\tmp.vcf Chromosome Position GeneName AminoAcidVariant VariantType -r D:\data\tmp.gtf D:\data\tmp.fasta

### Linux

1. Change to desired installation directory
2. > git pull git@github.com:childsish/sofia.git
3. (Optional) Add the installation directory to the environment variable PYTHONPATH or create a symbolic link to a bin directory in the PATH environment variable

Creating a new action
-------------------
New actions are implemented by creating a new Python class that inherits from the action class found in modules.action. A action consists of several concepts.
1. **The name of the action.** This is the name that is referred to from the command line and other actions. It is defined by the class variable "NAME".
2. **Resources used.** A list of the resource names that the action will use. These names are specified by the user on the command line. Resources are defined by the class variable "RESOURCES".
3. **Dependencies on other actions.** A list of the other actions or resources that this action depends on. Each dependent action is defined by three key:value pairs. The name of the dependent action is defined by the key "name", the class by the key "action" and the how the resources used by the current action are mapped to the dependent action by the key "resource_map". Dependencies are defined by the class variable "DEPENDENCIES".
4. **Calculating the action.** The function to actually calculate the desired action also needs to be defined. The arguments that are passed to it are determined by the names of the given dependencies. The function is defined by the class member "calculate".
5. **Formatting the results (optional).** The output of "calculate" can be formatted before the final output by the "format" function.

Design Philosophy
-----------------

Batteries included.

 * There should be as few library dependencies as possible.

The user has to change the resource data as little as possible.

 * This means that gzipped files can not be indexed as gzip indexing requires the file to be unzipped and re-zipped using tabix. Using tabix would also require an extra library

The tool should be easily extended.

 * The default state is not a one-size-fits-all solution. Different groups have different needs. However, it should be easily extended to accomodate new types of resources and actions.
 * As much adaptation as possible should be carried out on the command line.


Other considerations
--------------------

It is not intended to be a workflow engine.

It should be able to annotate any set of bioloical entities.

Give the resource types with initialisation?

-t name:TableResource:

Attempts to follow the guidelines set out in:
http://www.hgvs.org/mutnomen/


Multiple VCFs
-------------

-r name:dname -t name:multivcf

To Do
-----

Add documentation to all functions that raise Exceptions

To Test
-------

VCF <=> GTF
GTF <=> VCF
