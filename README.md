SoFIA
=====

Software for the Flexible Integration of Annotation (SoFIA) is a framework designed to make integrating information from multiple sources as easy and painless as possible. This is achieved through the use of a worflow engine capable of automatically resolving a workflow dedicated toward fulfilling a particular purpose from a parent template. In practice, this means that the user only needs to provide the resources they wish to draw their information from and the entities they wish to associate with their resources, and the framework will do the rest.

By default, vanilla SoFIA comes with a genomics workflow, capable of annotating variants and genes, and calculating sequence features. If different functionality is required, SoFIA has been designed to be extensible allowing the user to easily extend the current workflow or even create a whole new workflow for completely different purposes.

Installation
------------

### Dependencies

SoFIA requires [Python 2.7][python] to be installed.

The framework of SoFIA has no dependencies on external libraries. However, the default workflow has 'soft' dependencies on the [htslib][htslib] and [pysam][pysam] libraries for indexing various file formats. If either of these libraries is not installed, then the framework will resort to reading in the entire file. This can significantly slow down the framework.

### via Source

As a Python program, SoFIA does not need to be compiled. As such, you can simply download the source and run it. However, You will need to check manually for updates.

1. Download and unzip the compressed version from GitHub:
https://github.com/childsish/sofia/releases/latest
2. Extract the file to desired installation directory
3. (optional) Add the installation directory to the PATH environment variable.

### via Git

1. Change to desired installation directory
2. To install `git clone git@github.com:childsish/sofia.git`
3. (optional) Add the installation directory to the PATH environment variable.
4. To update: `git pull`

`sofia /home/user/tmp/tmp.vcf -e chromosome_id position gene_id amino_acid_variant variant_type -r /home/user/tmp/tmp.gtf /home/user/tmp/tmp.fasta`

Defining a template
-------------------

Templates are found in the `sofia/templates` directory. Each template has a directory with it's own name. There are three main locations in the template's directory.

1. `sofia/templates/<template_name>/steps`. All steps are defined in this directory.
2. `sofia/templates/<template_name>/entities.json`. Complex entity relationships are defined in this file.
3. `sofia/templates/<template_name>/data`. Default data for the template is placed in this directory.

### Defining steps

New steps are implemented by creating a new Python class that inherits from the `Step` class found in modules.step. A step consists of several concepts.

1. **The name of the step.** This is the name that is referred to from the command line and other steps. It is defined by the name of the class.
2. **Required entities.** A list of entities that the step will use. Required entities are defined by the class variable "IN".
3. **Provided entities.** A list of entities that the step will provide. Provided entities are defined by the class variable "OUT".
4. **Calculating the step.** The function to actually calculate the desired step also needs to be defined. The arguments that are passed to it are determined by the names of the given dependencies. The function is defined by the class member "calculate".

Example:
```python

    from sofia_.step import Step

    class GetCodonUSage(Step):

        IN = ['coding_sequence']
        OUT = ['codon_usage']

        def calculate(self, coding_sequence):
            codon_usage = {}
            for i in xrange(0, len(coding_sequence), 3):
                codon = coding_sequence[i:i+3]
                if codon not in codon_usage:
                    codon_usage[codon] = 0
                codon_usage[codon] += 1
            return codon_usage
```

### Defining resources

Resources are practically identical to steps, but they have no incoming entities and some extra details to match them to provided filenames is required. 

### Defining entities

New entities are just as simple to create. Any entities declared by the step (in the IN and OUT member variables) are automatically created. If complex relationships among the entities need to be defined, then the `entities.json` is used for this purpose.

The root json object is an array in which several associative arrays can be stored, each representing an entity with complex relationships. The entity is defined by the following key:pair values:

* **name**. This is the name of the entity that the framework uses to identify it. The current format for the name is underscore separated, lower-case words.
* **is_a** (optional). This is the name of a single other entity that this entity can be considered equivalent to. This equivalency is not bi-directional (e.g. a `variant` can be considered a `genomic_position` but a `genomic_position` can not be used as a `variant`).
* **has_a** (optional). This is a set of the other entities that this entity contains. It is implemented as an array of associative arrays where the associative array describes how to access the contained entity:
    * **name**. The name that the framework uses to identify the child entity.
    * **key**. The key that is used by the Python object to access the child entity.
    * **type**. The type of access to the child entity required. If it is an attibute of an object then this values should be `attr`. If it is a key in a dictionary then this value should be `item`.
* **description** (optional). A description of the entity used by the `sofia info` command.

Example:
```json

[
  {
    "name": "genomic_feature",
    "is_a": "genomic_interval",
    "has_a": [
      { "name": "gene_id", "key": "name", "type": "attr" }
    ],
    "description": "A model of transcribed DNA. This includes all alternative transcripts."
  }
]
```

Design Philosophy
-----------------

Batteries included.

 * There should be as few library dependencies as possible.

The user has to change the resource data as little as possible.
 
 * Ideally, all files can be used as-is. However, indexing the file is highly recommended as it will greatly speed up the framework. Indexing using the [htslib][htslib] is supported by default.

The tool should be easily extended.

 * The default state is not a one-size-fits-all solution. Different groups have different needs. However, it should be easily extended to accomodate new types of resources and steps.


Standardisation (Variant annotation)
------------------------------------

The genomic template that comes with SoFIA will use the major transcript when finding the variant effect on a gene. The major transcript is defined as the longest transcript (in coding nucleotides).

The template attempts to follow the guidelines laid out by the [Human Genome Variation Society][hgvs] when showing the coding and amino acid changes. However, we deviate from the guidelines by using only the 1-letter code for amino acids. Any other deviation is unintentional and should be brought to my attention.

The template also attempts to follow the [The Sequence Ontology][so] when describing the type of variant. Any deviation is unintentional and should be brought to my attention.


To Do
-----

There are still many ways in which SoFIA can be improved. Here are some that I plan to do, but I am always open to suggestions.

Refer to the GitHub [issues][issues] page for upcoming improvements, to make suggestions and bug submissions.

[python]: https://www.python.org/downloads/ "Download Python 2.7"
[htslib]: http://www.htslib.org/ "Download htslib"
[pysam]: https://code.google.com/p/pysam/ "Download pysam"
[hgvs]: http://www.hgvs.org/mutnomen/ "Human Genome Variation Society"
[so]: http://www.sequenceontology.org/ "The Sequence Ontology"
[issues]: https://github.com/childsish/sofia/issues "To Do"
