.. MWL documentation master file, created by
   sphinx-quickstart on Mon Mar  4 21:53:19 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ELDAmwl's documentation!
===================================

ELDAmwl is one of the modules of the
`Single Calculus Chain (SCC)
<https://scc-documentation.readthedocs.io/en/latest/index.html>`_.
Its purpose is the retrieval of optical
aerosol properties from multiwavelength
lidar data. The implemented algorithms
are based on the ELDA module (EARLINET
Lidar Data Analyzer). The improvement
of ELDAmwl is that the optical properties are not
derived independent of each other (as in the old ELDA module),
but synergies between the retrievals of
different product types at different wavelengths are used.
Further, the program design is modular and allows
the addition and replacement of algorithm components.


.. toctree::
    :caption: ELDAmwl Documentation
    :maxdepth: 2

    usage/usage
    installing/installing
    algorithms/algorithms
    contributing/contributing

.. toctree::
    :caption: Indices and tables
    :maxdepth: 2

    genindex
    modindex

.. toctree::
    :caption: API documentation
    :maxdepth: 2

    api/modules



