Attotree
==================================================================================


Introduction
------------

Rapid estimation of phylogenetic trees directly from FASTA files in the style of
`Mashtree <https://github.com/lskatz/mashtree>`_. With the default options,
its output is identical to Mashtree,
but the computation takes only a fraction of time.


Installation
------------

Using Bioconda
~~~~~~~~~~~~~~

.. code-block:: bash

    conda install -y -c bioconda -c conda-forge attotree


Using PyPI
~~~~~~~~~~

First, install the following dependencies:

* `Mash <https://github.com/marbl/Mash>`_
* `QuickTree <https://github.com/khowe/quicktree>`_


Then install the Attotree Python package:

.. code-block:: bash

    pip install -U attotree


Quick example
-------------

.. code-block:: bash

    conda install attotree
    attotree tests/*.fa


Command-line parameters
-----------------------


.. code-block::

    $ attotree -h

    Program: attotree (rapid estimation of phylogenetic trees using sketching)
    Version: 0.1.1
    Author:  Karel Brinda <karel.brinda@inria.fr>

    usage: attotree [-k INT] [-s INT] [-t INT] [-o FILE] [-f STR] [-L] genomes [genomes ...]

    positional arguments:
      genomes     input genome file (fasta / gzipped fasta / list of files when "-L")

    options:
      -h          show this help message and exit
      -v          show program's version number and exit
      -k INT      kmer size [21]
      -s INT      sketch size [10000]
      -t INT      number of threads [10]
      -o FILE     newick output [stdout]
      -f STR      tree inference algorithm (nj/upgma) [nj]
      -L          input files are list of files



Issues
------

Please use `Github issues <https://github.com/karel-brinda/attotree/issues>`_.


Changelog
---------

See `Releases <https://github.com/karel-brinda/attotree/releases>`_.


Licence
-------

`MIT <https://github.com/karel-brinda/attotree/blob/master/LICENSE.txt>`_


Authors
-------

`Karel Brinda <http://brinda.eu>`_ <karel.brinda@inria.fr>

