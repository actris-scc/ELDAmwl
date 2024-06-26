from copy import deepcopy

import numpy as np

from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from numpy import square as sqr


class CalcVldrVFreudenthaler22(BaseOperation):
    """class for numerical calculations of VLDR profiles according to the method described in
        `Freudenthaler 2016 <https://amt.copernicus.org/articles/9/4181/2016>`_ and
        `Freudenthaler 2021 <https://repositories.imaa.cnr.it/public/atmospheric_lidar_ghk>`_.

    Keyword Args:
        ~: the same as for `.CalcVLDRProfile`

    """

    name = 'CalcVldrVFreudenthaler22'
    sigratio = None
    depol_params = None

    def run(self, **kwargs):
        r"""calculates VLDR profile :math:`\delta (z)`

        from reflected and transmitted signals :math:`\widetilde{P_r}(t,z)` and :math:`\widetilde{P_t}(t,z)`

        The incoming signal ratio must be calculated from signals prepared with `.PrepareDepolSignals` before.

        The retrieval has the following steps:

        * the calibrated signal ratio :math:`\delta^*(z)` is derived from the signal ratio :math:`R(z)`

        .. math::
            \delta^*(z) &= R(z) \: \frac{K}{\eta^*}
                         = \frac{\widetilde{P_r}(z)}{\widetilde{P_t}(z)} \: \frac{K}{\eta^*} \\
            \Delta\delta^*(z) &= \Delta R(z) \: \frac{K}{\eta^*}\\

        * the VLDR :math:`\delta(z)` is

        .. math::
            \delta(z) &= \frac{\delta^*(z) \bigl( G_t + H_t \bigr) - \bigl( G_r + H_r \bigr) }
                              {\bigl( G_r - H_r \bigr) - \delta^*(z) \bigl( G_t - H_t \bigr)} \\
                      &= \frac{\delta^*(z) a - b }
                              {c - \delta^*(z) d} \\

        * the statistical uncertainty is:

        .. math::
            \Delta\delta(z) &= \Biggl\lvert\frac{\delta^*(z) a (1 - d) - b d + a c}
                                     { \bigl( c - \delta^*(z)d\bigr)^2} \:
                                     \Delta\delta^*(z) \Biggr\rvert\\

        * while the lower and upper bound of the systematic uncertainty are:

        .. math::
            \Delta\delta_{low}(z) &= a_{low} + b_{low}\delta(z) + c_{low}\delta^2(z) \\
            \Delta\delta_{up}(z) &= a_{up} + b_{up}\delta(z) + c_{up}\delta^2(z) \\

        Keyword Args:
            sigratio (xarray.DataSet): already smoothed signal ratio with data_vars:

                * 'data' :math:`R = \frac{P_r}{P_t}` = ratio of reflected to transmitted signals

                * 'error' :math:`\Delta R` = statistical absolute uncertainty of :math:`R`

                * 'qf', 'binres' = quality flag and bin resolution of :math:`R` (not used here)

                * 'molecular_depolarization_ratio' (not used here)

                * and others (not used here)

            depol_params (addict.Dict): dictionary with mandatory keys

                * 'gain_ratio' :math:`\eta^*`

                * 'gain_ratio_correction' :math:`K`

                * 'HR', 'HT', 'GR', 'GT' = H and G parameters of the reflected and transmitted signals (:math:`H_r`, :math:`H_t`, :math:`G_r`, :math:`G_t`)  # noqa E501

                * 'sys_err_lower_bound_a', 'sys_err_lower_bound_b', 'sys_err_lower_bound_c' = Parameters to calculate the lower bound of the systematic error (:math:`a_{low}`, :math:`b_{low}`, :math:`c_{low}`)  # noqa E501

                * 'sys_err_upper_bound_a', 'sys_err_upper_bound_b', 'sys_err_upper_bound_c' = Parameters to calculate the upper bound of the systematic error (:math:`a_{up}`, :math:`b_{up}`, :math:`c_{up}`)  # noqa E501

            Returns:
                VLDR profile (xarray.DataSet) with calculated data_vars:

                * 'data' = :math:`\delta(z)`

                * 'error' = :math:`\Delta\delta(z)`

                * 'sys_err_neg', 'sys_err_pos' = :math:`\Delta\delta_{low}(z)`, :math:`\Delta\delta_{up}(z)`

                * all other variables and attributes are copied from sigratio
        """
        assert 'sigratio' in kwargs
        assert 'depol_params' in kwargs

        sigratio = kwargs['sigratio']
        depol_params = kwargs['depol_params']

        # 1) calculate calibrated signal ratio

        calibr_factor = depol_params.gain_ratio_correction / depol_params.gain_ratio

        calibrated_sigratio = sigratio.data * calibr_factor
        calibrated_sigratio_err = sigratio.err * calibr_factor

        # 2) calculate volume depolarization ratio
        a = depol_params.GT + depol_params.HT
        b = depol_params.GR + depol_params.HR
        c = depol_params.GR - depol_params.HR
        d = depol_params.GT - depol_params.HT

        vldr_data = (calibrated_sigratio * a - b) / (c - calibrated_sigratio * d)

        vldr_data_sqr = sqr(vldr_data)

        vldr = deepcopy(sigratio)
        vldr['data'] = vldr_data

        vldr['err'] = np.absolute(
            (calibrated_sigratio * a * (1 - d) - b * d + a * c) / sqr(c - d * calibrated_sigratio)
            * calibrated_sigratio_err)

        # 3) calculate systematic errors
        vldr['sys_err_neg'] = depol_params.sys_err_lower_bound_a \
            + depol_params.sys_err_lower_bound_b * vldr_data \
            + depol_params.sys_err_lower_bound_c * vldr_data_sqr

        vldr['sys_err_pos'] = depol_params.sys_err_upper_bound_a \
            + depol_params.sys_err_upper_bound_b * vldr_data \
            + depol_params.sys_err_upper_bound_c * vldr_data_sqr

        # todo: test if the mol depol is available here
        vldr['molecular_depolarization_ratio'] = sigratio['mol_depolarization_ratio']

        return vldr


class CalcVLDRProfile(BaseOperationFactory):
    """creates a class for numerical calculations of volume linear depolarization ratio profiles
    from reflected and transmitted signal.

    Returns an instance of `.BaseOperation` which calculates the volume linear depolarization ratio
    from a transmitted and a reflected  signal. The keyword parameter are transferred to this instance.
    In this case, it will be always return an instance of `.CalcVldrVFreudenthaler22`.

    Keyword Args:
        prod_id (str): id of the product  # nopep8

    Returns:
        instance of `.BaseOperation`

    """

    name = 'CalcVLDRProfile'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(CalcVLDRProfile, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for the numerical VLDR calculations

        Returns:
            str: name of the class for the VLDR calculation. In this case, it always returns 'CalcVldrVFreudenthaler22'
        """
        return self.db_func.read_vldr_algorithm(self.prod_id)


registry.register_class(CalcVLDRProfile,
                        CalcVldrVFreudenthaler22.__name__,
                        CalcVldrVFreudenthaler22)
