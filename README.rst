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

:: code-block:: bash

    conda install -y -c bioconda -c conda-forge attotree


Using PyPI
~~~~~~~~~~

First, install the following dependencies:

* `Mash <https://github.com/marbl/Mash>`_
* `QuickTree <https://github.com/khowe/quicktree>`_


Then install the Attotree Python package:

:: code-block:: bash

    pip install -U attotree


Quick example
-------------

.. code-block:: bash

    conda install attotree
    attotree tests/*.fa


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

