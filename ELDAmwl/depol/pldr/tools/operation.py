import numpy as np

from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from numpy import square as sqr


class CalcPLDRProfileDefault(BaseOperation):
    """class for numerical calculations of PLDR profiles according to the method described in ?

    Keyword Args:
        ~: the same as for `.CalcPLDRProfile`

    """

    name = 'CalcPLDRProfileDefault'
    vldr = None
    rayl_depol = None
    bsc_ratio = None

    def run(self, **kwargs):
        r"""calculates PLDR profile :math:`\delta^{par}(t,z)`

        from VLDR :math:`\delta(t,z)`, molecular linear depolarization ratio :math:`\delta^{mol}(t,z)`,
        particle backscatter coefficient :math:`\beta^{par}(t,z)`, and
        backscatter ratio :math:`R(t,z) = 1 + \frac{\beta^{par}(t,z)}{\beta^{mol}(t,z)}`

        The retrieval has the following steps:

        * we define terms :math:`m`, :math:`v`, and :math:`d` (denominator)

        .. math::
            m(z) &= 1 + \delta^{mol}(z) \\
            v(z) &= 1 + \delta(z) \\
            d(z) &= m(z) \: R(z) - v(z) \\

        * the PLDR :math:`\delta^{par}(z)` is

        .. math::
            \delta^{par}(z) &= \frac{ m(z) \: \delta(z) \: R(z) - v \: \delta^{mol}(t,z) }
                                    { m(z) \: R(z) - v(z)} \\

        * the statistical uncertainty (for easier reading we omit z) is:

        .. math::
            \Delta \delta^{par} &= \sqrt{\Biggl( \frac{\partial \delta^{par}}
                                                      {\partial R} \Delta R
                                         \Biggr) ^ 2 +
                                         \Biggl( \frac{\partial \delta^{par}}
                                                      {\partial \delta} \Delta \delta
                                         \Biggr) ^ 2
                                        } \\

            \frac{\partial \delta^{par}}{\partial R} &= \frac{m v \: \bigl( \delta^{mol} - \delta \bigr)}
                                                             {d^2} \\
            \frac{\partial \delta^{par}}{\partial \delta} &= \frac{m^2 \bigl( R ^2 - R \bigr) + 2 v \delta^{mol}}
                                                                  {d^2} \\

        * The systematic uncertainty of :math:`\delta^{par}(t,z)` is not retrieved here.

        Keyword Args:
            vldr (xarray.DataSet): volume linear depolarization ratio with data_vars:

                * 'data' :math:`\delta` = volume linear depolarization ratio

                * 'error' :math:`\Delta\delta` = statistical absolute uncertainty of :math:`\delta`

                * 'qf', 'binres' = quality flag and bin resolution of :math:`\delta` (not used here)

                * 'molecular_depolarization_ratio' :math:`\delta^{mol}` = molecular linear depolarization ratio

                * and others (not used here)

            bsc_ratio (xarray.DataSet): backscatter ratio with data_vars:

                * 'data' :math:`R = 1 + \frac{\beta^{par}}{\beta^{mol}}` = backscatter ratio

                * 'error' :math:`\Delta R` = statistical absolute uncertainty of :math:`R`

                * 'qf', 'binres' = quality flag and bin resolution of :math:`R` (not used here)

                * and others (not used here)

            Returns:
                PLDR profile (xarray.DataSet) with calculated data_vars:

                * 'data' = :math:`\delta^{par}(z)`

                * 'error' = :math:`\Delta\delta^{par}(z)`

                * 'sys_err_neg’, ‘sys_err_pos’ = np.nan

                * all other variables and attributes are copied from vldr
        """

        assert 'vldr' in kwargs
        assert 'bsc_ratio' in kwargs
        assert 'calc_params' in kwargs

        calc_stat_err = kwargs['calc_params']['calc_stat_err']

        vldr = kwargs['vldr'].data
        vldr_err = kwargs['vldr'].err
        mldr = kwargs['vldr'].molecular_depolarization_ratio

        R = kwargs['bsc_ratio'].data
        R_err = kwargs['bsc_ratio'].err

        # 1) calculate m, v, d
        m = 1 + mldr
        v = 1 + vldr
        d = m * R - v

        # 1) PLDR
        pldr_data = (m * vldr * R - v * mldr) / d

        # 2) calculate statistical error
        if calc_stat_err:
            err_from_R = (m * v * (mldr - vldr)) / d**2 * R_err
            err_from_vldr = (m**2 * (R**2 - R) + 2 * v * mldr) / d**2 * vldr_err
            pldr_err = np.sqrt(err_from_R**2 + err_from_vldr**2)
        else:
            pldr_err = vldr_err * np.nan

        pldr = kwargs['vldr'].copy(deep=True)
        pldr['data'] = pldr_data
        pldr['err'] = pldr_err
        pldr['sys_err_neg'][:] = np.nan
        pldr['sys_err_pos'][:] = np.nan

        return pldr


class CalcPLDRProfile(BaseOperationFactory):
    """creates a class for numerical calculations of particle linear depolarization ratio profiles
    from volume depolarization and particle backscatter profiles.

    Returns an instance of `.BaseOperation` which calculates the particle linear depolarization ratio
    from a volume depolarization and particle backscatter. The keyword parameter are transferred to this instance.
    In this case, it will be always return an instance of `.CalcPldrDefault`.

    Keyword Args:
        prod_id (str): id of the product  # nopep8

    Returns:
        instance of `.BaseOperation`

    """

    name = 'CalcPLDRProfile'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(CalcPLDRProfile, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for the numerical PLDR calculations

        Returns:
            str: name of the class for the PLDR calculation. In this case, it always returns 'CalcPLDRProfileDefault'
        """
        return CalcPLDRProfileDefault.__name__


registry.register_class(CalcPLDRProfile,
                        CalcPLDRProfileDefault.__name__,
                        CalcPLDRProfileDefault)
