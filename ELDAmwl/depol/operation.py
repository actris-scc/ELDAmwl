from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.interface import IVLDROp
from ELDAmwl.component.registry import registry
from ELDAmwl.depol.product import VLDRs
from ELDAmwl.depol.tools.operation import CalcVLDRProfile
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import MC

import zope


class VLRDFactory(BaseOperationFactory):
    """creates a factory for the retrieval of VLDR profiles.

    in this case, it always returns an instance of `.VLRDFactoryDefault`

    """

    name = 'VLRDFactory'

    def __call__(self, **kwargs):
        assert 'vldr_param' in kwargs
        res = super(VLRDFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """read from database (or other sources) which class to create

        Returns: always "VLRDFactoryDefault"

        """
        return VLRDFactoryDefault.__name__


class VLRDFactoryDefault(BaseOperation):
    """ a factory class that derives a single instance of `.VLDRs` .

    This factory class handles the different use cases.

    Keyword Args:
        vldr_param (`.VLDRParams`): parameters for the retrieval of the VLDR
    """

    name = 'VLRDFactoryDefault'

    data_storage = None
    transm_sig = None
    refl_sig = None
    sig_ratio = None
    param = None
    empty_vldr = None
    prod_id = None

    def prepare(self):
        self.param = self.kwargs['vldr_param']
        self.prod_id = self.param.prod_id_str

        if not self.param.includes_product_merging():
            self.transm_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.transm_sig_id_str)
            self.refl_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.refl_sig_id_str)

            self.param.add_params_from_signal(self.transm_sig)
            self.param.add_params_from_signal(self.refl_sig)

        self.sig_ratio = Signals.as_sig_ratio(self.refl_sig, self.transm_sig)

        self.empty_vldr = VLDRs.init(
            self.sig_ratio, self.param)

    def get_non_merge_product(self):

        vldr_retrieval_routine = CalcVLDR()(
            vldr_params=self.param,
            calc_routine=CalcVLDRProfile()(prod_id=self.prod_id),
            signal_ratio=self.sig_ratio,
            empty_vldr=self.empty_vldr,
        )
        vldr = vldr_retrieval_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(vldr_retrieval_routine, IMonteCarlo)
            vldr.err[:] = adapter(self.param.mc_params)
        else:
            vldr = vldr

        del self.sig_ratio
        del self.refl_sig
        del self.transm_sig

        return vldr

    def get_product(self):
        """ organizes the usecases and retrieves the products

        Returns: `.VLDRs`: a time series of volume linear depolarization ratio profiles

        """
        self.prepare()

        if not self.param.includes_product_merging():
            vldr = self.get_non_merge_product()
        else:
            vldr = None

        vldr.quality_control()

        return vldr


class CalcVLDR(BaseOperationFactory):
    """
    creates a Class for the calculation of an instance of `.VLDRs`.

    Returns an instance of `.BaseOperation` which calculates the volume linear depolarization ratio
    from a transmitted and a reflected  signal. The keyword parameter are transferred to this instance.
    In this case, it will be always return an instance of `.CalcVLDRDefault`.

    Keyword Args:
        vldr_params (`.VLDRParams`): retrieval parameter of the VLDR product
        calc_routine (`.BaseOperation`): result of `.CalcVLDRProfile`
        signal_ratio (`.Signals`): ratio between the reflected and the transmitted signals
        empty_vldr (`.VLDRs`): instance of VLDRs which has all meta data but profile data are empty arrays

    Returns:
        instance of `.BaseOperation`

    """

    name = 'CalcVLDR'

    def __call__(self, **kwargs):
        assert 'vldr_params' in kwargs
        assert 'calc_routine' in kwargs
        assert 'signal_ratio' in kwargs
        assert 'empty_vldr' in kwargs

        res = super(CalcVLDR, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcVLDRDefault' .
        """
        return 'CalcVLDRDefault'


@zope.interface.implementer(IVLDROp)
class CalcVLDRDefault(BaseOperation):
    """Calculates VLDRs from the ratio of a reflected and a transmitted signal.

    The result is a copy of empty_vldr, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        vldr_params (`.VLDRParams`): \
                retrieval parameter of the VLDR product
        calc_routine (`.BaseOperation`): result of `.CalcVLDRProfile`
        signal_ratio (`.Signals`): signal ratio
        empty_vldr (`.VLDRs`): \
                instance of VLDRs which has all meta data but profile data are empty arrays

    Returns:
        `.VLDRs`: profiles of volume linear depolarization ratios

    """

    name = 'CalcVLDRDefault'

    vldr_params = None
    sig_ratio = None
    calc_routine = None
    result = None

    def __init__(self, **kwargs):
        super(CalcVLDRDefault, self).__init__(**kwargs)
        self.sig_ratio = self.kwargs['signal_ratio']
        self.calc_routine = self.kwargs['calc_routine']
        self.vldr_params = self.kwargs['vldr_params']
        self.result = deepcopy(self.kwargs['empty_vldr'])

    def run(self, data=None):
        r""" collects all parameters for VLDR calculation and run the calculator class `.CalcVLDRProfile`.

        The the optional keyword arg 'data' allows to feed new signal ratios into
        an existing instance of CalcVLDRDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Note: Even if this class does not do much, it is necessary for the MC infrastructure.

        The following parameters are collected for the retrieval

        * :math:`\eta^*` : the gain ratio is taken from the ELPP file

        * :math:`K`: the gain ratio correction parameter is taken from the database table `.PolarizationCalibrationCorrectionFactors`  # noqa E

        * :math:`H_r` and :math:`H_t` are the :math:`H` parameters of the reflected and transmitted signal, respectively. They are taken from the ELPP file.

        * :math:`G_r` and :math:`G_t` are the :math:`G` parameters of the reflected and transmitted signal, respectively. They are taken from the ELPP file.

        Keyword Args:
            data (`.Signals`): signal ratios, default=None

        Returns:
            `.VLDRs`: profiles of volume linear depolarization ratios

        """
        if data is None:
            data = self.sig_ratio

        # extract relevant parameter for calculation of VLDR into Dict

        params = Dict({'gain_ratio': data.pol_calibr.gain_factor.value,
                       'gain_ratio_correction': data.pol_calibr.gain_factor_correction.value,
                       'HT': self.vldr_params.crosstalk_h_transm,
                       'HR': self.vldr_params.crosstalk_h_refl,
                       'GT': self.vldr_params.crosstalk_g_transm,
                       'GR': self.vldr_params.crosstalk_g_refl,
                       'sys_err_lower_bound_a': self.vldr_params.depol_uncertainty_params.a_lower,
                       'sys_err_lower_bound_b': self.vldr_params.depol_uncertainty_params.b_lower,
                       'sys_err_lower_bound_c': self.vldr_params.depol_uncertainty_params.c_lower,
                       'sys_err_upper_bound_a': self.vldr_params.depol_uncertainty_params.a_upper,
                       'sys_err_upper_bound_b': self.vldr_params.depol_uncertainty_params.b_upper,
                       'sys_err_upper_bound_c': self.vldr_params.depol_uncertainty_params.c_upper,
                       })

        # todo: propagate systematic errors through all operations, smoothing etc.
        self.result.ds = self.calc_routine.run(
            sigratio=data.ds,
            depol_params=params)
        self.result.profile_qf = deepcopy(data.profile_qf)

        return self.result


registry.register_class(VLRDFactory,
                        VLRDFactoryDefault.__name__,
                        VLRDFactoryDefault)

registry.register_class(CalcVLDR,
                        CalcVLDRDefault.__name__,
                        CalcVLDRDefault)
