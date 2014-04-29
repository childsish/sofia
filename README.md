ebias
=====

Extensible BioInformation Aggregation System

example command:

> python ebias.py D:\data\tmp.vcf chr pos gene_name chr_mut aa_mut -r mdl=D:\data\tmp.gtf seq=D:\data\tmp.fasta gcode=D:\data\tmp.gc

Creating a new feature
----------------------
New features are implemented by creating a new Python class that inherits from the Feature class found in modules.feature. A feature consists of several concepts.
1. **The name of the feature.** This is the name that is referred to from the command line and other features. It is defined by the class variable "NAME".
2. **Resources used.** A list of the resource names that the feature will use. These names are specified by the user on the command line. Resources are defined by the class variable "RESOURCES".
3. **Dependencies on other features.** A list of the other features or resources that this feature depends on. Each dependent feature is defined by three key:value pairs. The name of the dependent feature is defined by the key "name", the class by the key "feature" and the how the resources used by the current feature are mapped to the dependent feature by the key "resource_map". Dependencies are defined by the class variable "DEPENDENCIES".
4. **Calculating the feature.** The function to actually calculate the desired feature also needs to be defined. The arguments that are passed to it are determined by the names of the given dependencies. The function is defined by the class member "calculate".
5. **Formatting the results (optional).** The output of "calculate" can be formatted before the final output by the "format" function.

