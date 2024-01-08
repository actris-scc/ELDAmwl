=======
ELDAmwl
=======

.. image:: https://github.com/actris-scc/ELDAmwl/actions/workflows/main.yml/badge.svg
   :target: https://coveralls.io/github/actris-scc/ELDAmwl?branch=master
   :alt: Testing Status

.. image:: https://img.shields.io/coveralls/github/actris-scc/ELDAmwl/master.svg
   :target: https://coveralls.io/github/actris-scc/ELDAmwl?branch=master
   :alt: Coverage Status

.. image:: https://img.shields.io/readthedocs/eldamwl.svg
   :target: http://ELDAmwl.readthedocs.io
   :alt: Documentation

.. image:: https://api.codeclimate.com/v1/badges/c8b0acac8032573b8a7a/maintainability
   :target: https://codeclimate.com/github/actris-scc/ELDAmwl/maintainability
   :alt: Maintainability


ELDAmwl is a Python software for retrieving vertical profiles of optical aerosol properties at multiple wavelengths
from lidar measurements. It is one module of the Single Calculus Chain (SCC)
[`D'Amico et. al. (2015) <https://amt.copernicus.org/articles/8/4891/2015/>`_] .
ELDAmwl reads pre-processed lidar signals [`D'Amico et. al. (2016) <https://amt.copernicus.org/articles/9/491/2016/>`_],
derives particle backscatter and extinction coefficients, volume and particle linear depolarization ratios,
lidar ratios and Angström exponents.
It is an enhancement of the EARLINET Lidar Data Analyzer ELDA
[`Mattis et al. (2016) <https://amt.copernicus.org/articles/9/3009/2016/>`_] which makes synergistic use of the
multiwavelength information of the lidar data.
