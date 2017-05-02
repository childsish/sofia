[![Build Status](https://travis-ci.org/childsish/sofia.svg?branch=master)](https://travis-ci.org/childsish/sofia)

SoFIA
=====

Software for the Flexible Integration of Annotation (SoFIA) is a framework designed to make integrating information from multiple sources as easy and painless as possible. This is achieved through the use of a worflow engine capable of automatically resolving a workflow dedicated toward fulfilling a particular purpose from a parent template. In practice, this means that the user only needs to provide the resources they wish to draw their information from and the entities they wish to associate with their resources, and the framework will do the rest.

By default, vanilla SoFIA comes with a genomics workflow, capable of annotating variants and genes, and calculating sequence features. If different functionality is required, SoFIA has been designed to be extensible allowing the user to easily extend the current workflow or even create a whole new workflow for completely different purposes.

There is a [Google Group][google-group] for discussions about SoFIA.  

Installation
------------

SoFIA requires [Python 3][python] to be installed with the pip package management system. Pip should come with the latest Python.

1. Open the command line with administrator priveleges (Powershell in Windows, Shell in Linux)
2. Update pip:
    * Windows: `python -m pip install -U pip setuptools`
    * Linux: `pip install -U pip setuptools`
3. Install SoFIA:
    * Windows: `python -m pip install sofia`
    * Linux: `pip install sofia`

Running SoFIA
-------------

We provide example data to help familiarise yourself with SoFIA. To get the data, run:

`python -m sofia get http://childsish.github.io/static/sofia/example.tar.gz`

To try the example, run:

`python -m sofia execute -e chromosome_id -e position -e gene_id -e amino_acid_variant -e variant_effect -r ./example/data/randome.gff -r ./example/data/randome.fasta -r ./example/data/randome.vcf variants -t variants -o output.txt -p 1`

The command line can be broken down into several parts:

1. `python -m sofia` Call the SoFIA script.
2. `execute` Build a template then resolve and run a workflow.
3. Define provided entities (resources):
   * `-r ./data/example/randome.gff features`. Provide a resource containing genomic features. Call it "features".
   * `-r ./data/example/randome.fasta sequences`. Provide a resource containing chromosome sequences. Call it "sequence".
   * `-r ./data/example/randome.vcf variants`. Provide a resource containing variants. Call it "variants".
4. `-e chromosome_id -e position -e gene_id -e amino_acid_variant -e variant_effect`. Annotate each variant with the chromosome, position, gene name, amino acid variant and variant effect.
5. `-t variants`. Declare the "variants" resource as the target. This means each variant gets annotated with the requested entities.

The output will be placed in the current directory in the `output.txt` file. To check if you got the correct output, run:

`diff ./example/data/output.txt output.txt`

### Data download scripts

SoFIA does not package any further data internally as you know best what is required your own analyses. However, to help you get started, we provide shell scripts in the `scripts` directory that download the basic necessities for annotation. If you wish for further "standard" annotation sets to be added, please let us know the url of each file or provide us a shell script and we will consider adding it to the default SoFIA installation.

Available:
 * GRCh37 version of the human genome

Using the API
-------------

SoFIA can also be used programatically. To use SoFIA, you must build a template, resolve a workflow from the template, then the workflow can be executed.

```python
from sofia.tools.build import build
from sofia.tools.resolve import resolve
from sofia.tools.execute import execute

template_directories = ['path_to_template_1', 'path_to_template_2']
provided_entity_definitions = ['provided_entity_1', 'provided_entity_2']
requested_entity_definitions = ['requested_entity_1', 'requested_entity_2']
template = build(template_directories)
provided_entities = [template.parser.parse_provided_entity(definition) for definition in provided_entity_definitions]
requested_entities = [template.parser.parse_requested_entity(definition) for definition in requested_entity_definitions]
workflow = resolve(template, provided_entities, requested_entities)
execute(workflow)
```

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
from sofia.step import Step

class GetCodonUSage(Step):

    IN = ['coding_sequence']
    OUT = ['codon_usage']

    def calculate(self, coding_sequence):
        codon_usage = {}
        for i in range(0, len(coding_sequence), 3):
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
[hgvs]: http://www.hgvs.org/mutnomen/ "Human Genome Variation Society"
[so]: http://www.sequenceontology.org/ "The Sequence Ontology"
[issues]: https://github.com/childsish/sofia/issues "To Do"
[google-group]: https://groups.google.com/forum/#!forum/workflows-on-demand
[vbox]: https://www.virtualbox.org/wiki/Downloads
[mint]: http://www.linuxmint.com/download.php
