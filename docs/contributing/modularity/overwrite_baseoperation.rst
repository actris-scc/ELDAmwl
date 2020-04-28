Overwrite an existing algorithm subsystem
-----------------------------------------

It might occur that a developer wants to completely overwrite an existing
algorithm subsystem. This option should be used only for subsystems for which no
user-selectable alternatives are foreseen, eg., the
:doc:`preparation of signals for the
extinction retrieval <example_SignalSlope>` .

Step 1
^^^^^^
In a first step, you need to add a new module
:mod:`ELDAmwl.plugins.PrepareExtSignalsBetter`
in the directory `ELDAmwl.plugins`.

In this module, you can create a new class and register it
with the ``override=True`` directive.

.. code:: python

    # -*- coding: utf-8 -*-
    """plugin for preparation of ELPP for extinction retrieval"""

    from ELDAmwl.factory import BaseOperation
    from ELDAmwl.prepare_signals import PrepareExtSignals
    from ELDAmwl.registry import registry
    from ELDAmwl.registry import registry

    class PrepareExtSignalsBetter(BaseOperation):

        name = 'PrepareExtSignalsBetter'

        def __init__(self, **kwargs):
            logger.debug('create PrepareExtSignalsBetter ')

        def run(self, **kwargs):
            logger.debug('run PrepareExtSignalsBetter ')


    registry.register_class(PrepareExtSignals,
                            PrepareExtSignalsBetter.__name__,
                            PrepareExtSignalsBetter,
                            override=True)


.. note::

    The new class needs to have a name attribute, and a run() method
    which accepts keyword arguments.

Step 2
^^^^^^

In a last step, the new module needs to be announced to the ELDAmwl package.
This is done by adding an import statement into the :mod:`ELDAmwl.plugins.plugin` module.

.. code:: python

    # -*- coding: utf-8 -*-
    """import of all plugins"""

    import ELDAmwl.plugins.PrepareExtSignalsBetter



