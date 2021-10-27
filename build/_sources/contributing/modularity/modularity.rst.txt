Modularity
==========

The modularity and expandability of ELDAmwl allows external developers to easily
add or replace algorithm subsystems without modifying the existing code.
The modularity is based on two classes:

* :class:`ELDAmwl.factory.BaseOperationFactory` for selecting which algorithm to use.
* :class:`ELDAmwl.factory.BaseOperation` containing the algorithm.

They represent a layered system, like a Matryoshka.

:class:`ELDAmwl.factory.BaseOperationFactory` is the outer
layer which is called by the surrounding code.
The only purpose of the descendants of this class is to
generate an instance of :class:`ELDAmwl.factory.BaseOperation`
(the core). For doing so, it checks which alternative
implementations of the corresponding algorithm subsystem
are available and returns the right one.

Additional alternative algorithm subsystems can be introduced by

.. toctree::
    :maxdepth: 1

    adding an user-selectable algorithm <add_new_baseoperation>
    overwriting an existing algorithm <overwrite_baseoperation>

.. toctree::
    :hidden:

    The global registry <registry>

.. note::
    All calculation etc. are performed by descendants of
    :class:`ELDAmwl.factory.BaseOperation`. The instances of
    :class:`ELDAmwl.factory.BaseOperationFactory` are just
    for making the choice among algorithms.

.. note::
    Instances of :class:`ELDAmwl.factory.BaseOperation` must never
    addressed directly. Always call the :class:`ELDAmwl.factory.BaseOperationFactory`.

:doc:`The global registry <registry>`

The link between the instances of :class:`ELDAmwl.factory.BaseOperationFactory`
and their corresponding :class:`ELDAmwl.factory.BaseOperation`
are handled in a global instance of :class:`ELDAmwl.registry.Registry`.

A list of all modularized algorithm subsystems can be found
:doc:`here <list_of_subsystems>`.

There are different levels of BaseOperation classes:

.. toctree::
    :maxdepth: 2

    baseoperation_complex
    baseoperation_basic
    baseoperation_fundamental

.. toctree::
    :hidden:

    examples


