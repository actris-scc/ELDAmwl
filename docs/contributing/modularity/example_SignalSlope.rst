Example of an additional user-selectable algorithm subsystem
------------------------------------------------------------

An example of user-selectable algorithm subsystems is the method for
the calculation of the
signal slope in the extinction retrieval.
Actually, there are two options available:

* weighted linear fit
* non-weighted linear fit

The user can select in the SCC interface, which of them shall be applied.
This decision is stored in the SCC database.
The corresponding table `_ext_methods` looks like

.. image:: table_ext_methods_2.png

The third column (`python_classname`) provides the exact name
of the corresponding :class:`ELDAmwl.bases.factory.BaseOperation` classes.

The BaseOperationFactory class for the retrieval of the signal slope
:class:`ELDAmwl.extinction.tools.operation.SignalSlope`
is implemented as follows:

.. code:: python

    from ELDAmwl.database.db_functions import read_extinction_algorithm
    from ELDAmwl.bases.factory import BaseOperationFactory


    class SignalSlope(BaseOperationFactory):
        """
        Creates a Class for the calculation of signal slope.

        Keyword Args:
            prod_id (str): id of the product
        """

        name = 'SignalSlope'
        prod_id = NC_FILL_STR

        def __call__(self, **kwargs):
            assert 'prod_id' in kwargs
            self.prod_id = kwargs['prod_id']

            res = super(SignalSlope, self).__call__(**kwargs)
            return res

        def get_classname_from_db(self):
            return read_extinction_algorithm(self.prod_id)


The function :meth:`ELDAmwl.database.db_functions.read_extinction_algorithm`
reads the class name of the :class:`ELDAmwl.bases.factory.BaseOperation` to be used for the
actual product from the SCC database.

The two available BaseOperation classes
(:class:`ELDAmwl.extinction.tools.operation.WeightedLinearFit` and
:class:`ELDAmwl.extinction.tools.operation.NonWeightedLinearFit`) are implemented as follows:

.. code:: python

    from ELDAmwl.bases.factory import BaseOperation


    class WeightedLinearFit(BaseOperation):
        """

        """
        name = 'WeightedLinearFit'

        def __init__(self, **kwargs):
            super(WeightedLinearFit, self).__init__(**kwargs)
            self.fit = LinFit(weight=True)

        def run(self, **kwargs):
            """

            Keyword Args:
                signal: addict.Dict with the keys 'x_data', 'y_data', 'yerr_data'
                which are all np.array

            Returns:
                addict.Dict with keys 'slope' and 'slope_err'

            """
            assert 'signal' in kwargs

            return self.fit.run(signal=kwargs['signal'])


    class NonWeightedLinearFit(BaseOperation):
        """
        calculates a non-weighted linear fit

        """
        name = 'NonWeightedLinearFit'

        def __init__(self, **kwargs):
            super(NonWeightedLinearFit, self).__init__(**kwargs)
            self.fit = LinFit(weight=False)

        def run(self, **kwargs):
            """
            starts the fit

            Keyword Args:
                signal: addict.Dict with the keys 'x_data', 'y_data', 'yerr_data'
                which are all np.array

            Returns:
                addict.Dict with keys 'slope' and 'slope_err'

            """
            assert 'signal' in kwargs
            return self.fit.run(signal=kwargs['signal'])


Finally, the BaseOperation classes needs to be registered.

.. code:: python

    registry.register_class(SignalSlope,
                        NonWeightedLinearFit.__name__,
                        NonWeightedLinearFit)

    registry.register_class(SignalSlope,
                        WeightedLinearFit.__name__,
                        WeightedLinearFit)

The calculation of the signal slope is called like

.. code:: python

        slope_routine = SignalSlope()(prod_id=any_prod_id_str)
        for t in range(times):
            for lev in range(levels):
                # fb = first bin of the fit window
                # lb = last bin of the fit window
                window_data = Dict({'x_data': x_data[t, fb:lb+1],
                                        'y_data': y_data[t, fb:lb+1],
                                        'yerr_data': yerr_data[t, fb:lb+1],
                                        })

                sig_slope = slope_routine.run(signal=window_data)


