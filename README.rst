Attotree
========

.. |info-badge| image:: https://img.shields.io/badge/Project-Info-blue
    :target: https://github.com/karel-brinda/attotree
.. |github-release-badge| image:: https://img.shields.io/github/release/karel-brinda/attotree.svg
    :target: https://github.com/karel-brinda/attotree/releases/
.. |pypi-badge| image:: https://img.shields.io/pypi/v/attotree.svg
    :target: https://pypi.org/project/attotree/
.. |doi-badge| image:: https://zenodo.org/badge/DOI/110.5281/zenodo.10945896.svg
    :target: https://doi.org/10.5281/zenodo.10945896
.. |ci-tests-badge| image:: https://github.com/karel-brinda/attotree/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/karel-brinda/attotree/actions/

|info-badge| |github-release-badge| |pypi-badge| |doi-badge| |ci-tests-badge|


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
    Version: 0.1.6
    Author:  Karel Brinda <karel.brinda@inria.fr>

    usage: attotree [-k INT] [-s INT] [-t INT] [-o FILE] [-m STR] [-d DIR] [-L] [-D] [-V] genome [genome ...]

    positional arguments:
      genome      input genome file(s) (fasta / gzipped fasta / list of files when "-L")

    options:
      -h          show this help message and exit
      -v          show program's version number and exit
      -k INT      kmer size [21]
      -s INT      sketch size [10000]
      -t INT      number of threads [#cores, 10]
      -o FILE     newick output [-]
      -m STR      tree construction method (nj/upgma) [nj]
      -d DIR      tmp dir [default system, /var/folders/z6...]
      -L          input files are list of files
      -D          debugging (don't remove tmp dir)
      -V          verbose output

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
