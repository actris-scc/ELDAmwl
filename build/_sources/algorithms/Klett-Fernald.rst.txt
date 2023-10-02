*************
Klett-Fernald
*************

.. math::

    \beta_{part}(r) &= \frac{A(r)}{B - 2 S A_{int}} - \beta_{mol}(r) \\
    A &= P(r) * \exp(-2(S_{par} - S_{mol}) M(r)) \\
    M(r) &= \int_{r_{ref}}^{r} \beta_{mol}(R) \mathrm{d}R \\
    A_{int} &= \int_{r_{ref}}^{r} A(R) \mathrm{d}R \\
    B &= \frac{ P(r_{ref}) }{\beta_{part}(r_{ref})  + \beta_{mol}(r_{ref})}

with
:math:`\beta_{par}`, :math:`\beta_{mol}`: backscatter coeffcient of particles and molecules, respectively

:math:`S_{par}`, :math:`S_{mol}`: lidar ratio of particles and molecules, respectively

:math:`P(r)`: prepared signal

:math:`r`, :math:`R`: range

:math:`r_{ref}`: reference (calibration) range
