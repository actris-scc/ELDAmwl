from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.interface import IPLDROp
from ELDAmwl.component.registry import registry
from ELDAmwl.depol.pldr.product import PLDRs
from ELDAmwl.depol.pldr.tools.operation import CalcPLDRProfile
from ELDAmwl.utils.constants import MC

import zope

class PLDRFactory(BaseOperationFactory):
    """creates a factory for the retrieval of PLDR profiles.

    in this case, it always returns an instance of `.PLRDFactoryDefault`

    """

    name = 'PLDRFactory'

    def __call__(self, **kwargs):
        assert 'pldr_param' in kwargs
        assert 'resolution' in kwargs
        res = super(PLDRFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """read from database (or other sources) which class to create

        Returns: always "PLRDFactoryDefault"

        """
        return PLDRFactoryDefault.__name__


class PLDRFactoryDefault(BaseOperation):
    """ a factory class that derives a single instance of `.PLDRs` .

    This factory class handles the different use cases.

    Keyword Args:
        pldr_param (`.PLDRParams`): parameters for the retrieval of the PLDR
    """

    name = 'PLDRFactoryDefault'

    data_storage = None
    vldr = None
    bsc = None
    param = None
    empty_pldr = None
    prod_id = None
    resolution = None

    def prepare(self):
        self.param = self.kwargs['pldr_param']
        self.resolution = self.kwargs['resolution']
        self.prod_id = self.param.prod_id_str

        # if not self.param.includes_product_merging():
        #     self.transm_sig = self.data_storage.prepared_signal(
        #         self.param.prod_id_str,
        #         self.param.transm_sig_id_str,
        #         self.resolution)
        #     self.refl_sig = self.data_storage.prepared_signal(
        #         self.param.prod_id_str,
        #         self.param.refl_sig_id_str,
        #         self.resolution)
        #
        #     self.param.add_params_from_signal(self.transm_sig)
        #     self.param.add_params_from_signal(self.refl_sig)
        #
        # self.sig_ratio = Signals.as_sig_ratio(self.refl_sig, self.transm_sig)
        #
        self.empty_pldr = PLDRs.init(
            self.vldr, self.bsc, self.param)

    def get_non_merge_product(self):

        pldr_retrieval_routine = CalcPLDR()(
            pldr_params=self.param,
            calc_routine=CalcPLDRProfile()(prod_id=self.prod_id),
            vldr=self.vldr,
            bsc=self.bsc,
            empty_pldr=self.empty_pldr,
        )
        pldr = pldr_retrieval_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(pldr_retrieval_routine, IMonteCarlo)
            pldr.err[:] = adapter(self.param.mc_params)
        else:
            pldr = pldr

        del self.vldr
        del self.bsc
        del self.empty_pldr

        return pldr

    def get_product(self):
        """ organizes the usecases and retrieves the products

        Returns: `.VLDRs`: a time series of volume linear depolarization ratio profiles

        """
        self.prepare()

        if not self.param.includes_product_merging():
            pldr = self.get_non_merge_product()
        else:
            pldr = None

        return pldr


class CalcPLDR(BaseOperationFactory):
    """
    creates a Class for the calculation of an instance of `.PLDRs`.

    Returns an instance of `.BaseOperation` which calculates the particle linear depolarization ratio
    from a volume depolarization ratio and a particle backscatter.
    The keyword parameter are transferred to this instance.
    In this case, it will be always return an instance of `.CalcPLDRDefault`.

    Keyword Args:
        pldr_params (`.PLDRParams`): retrieval parameter of the PLDR product
        calc_routine (`.BaseOperation`): result of `.CalcPLDRProfile`
        vldr (`.VLDRs`): volume linear depolarization ratio
        bsc (`.Backscatters`): particle backscatter coefficient
        empty_pldr (`.PLDRs`): instance of PLDRs which has all meta data but profile data are empty arrays

    Returns:
        instance of `.BaseOperation`

    """

    name = 'CalcPLDR'

    def __call__(self, **kwargs):
        assert 'pldr_params' in kwargs
        assert 'calc_routine' in kwargs
        assert 'vldr' in kwargs
        assert 'bsc' in kwargs
        assert 'empty_pldr' in kwargs

        res = super(CalcPLDR, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcPLDRDefault' .
        """
        return 'CalcPLDRDefault'


@zope.interface.implementer(IPLDROp)
class CalcPLDRDefault(BaseOperation):
    """Calculates PLDRs from the volume linear depolarization and particle backscatter.

    The result is a copy of empty_pldr, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        pldr_params (`.PLDRParams`): \
                retrieval parameter of the PLDR product
        calc_routine (`.BaseOperation`): result of `.CalcPLDRProfile`
        vldr (`.VLDRs`): volume depolarization ratio
        bsc (`.Backscaters`): particle backscatter coefficient
        empty_pldr (`.PLDRs`): \
                instance of PLDRs which has all meta data but profile data are empty arrays

    Returns:
        `.PLDRs`: profiles of particle linear depolarization ratios

    """

    name = 'CalcPLDRDefault'

    pldr_params = None
    vldr = None
    bsc = None
    calc_routine = None
    result = None

    def __init__(self, **kwargs):
        super(CalcPLDRDefault, self).__init__(**kwargs)
        self.vldr = self.kwargs['vldr']
        self.bsc = self.kwargs['bsc']
        self.calc_routine = self.kwargs['calc_routine']
        self.pldr_params = self.kwargs['pldr_params']
        self.result = self.kwargs['empty_pldr'].copy()

    def run(self, data=None):
        r""" collects all parameters for PLDR calculation and run the calculator class `.CalcPLDRProfile`.

        The the optional keyword arg 'data' allows to feed new svldr and bsc into
        an existing instance of CalcPLDRDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Note: Even if this class does not do much, it is necessary for the MC infrastructure.

        The following parameters are collected for the retrieval

        Keyword Args:
            data (`.Signals`): signal ratios, default=None

        Returns:
            `.PLDRs`: profiles of particle linear depolarization ratios

        """
        if data is None:
            data = self.sig_ratio

        # extract relevant parameter for calculation of VLDR into Dict

        # params = Dict({'gain_ratio': data.pol_calibr.gain_factor.value,
        #                'gain_ratio_correction': data.pol_calibr.gain_factor_correction.value,
        #                'HT': self.vldr_params.crosstalk_h_transm,
        #                'HR': self.vldr_params.crosstalk_h_refl,
        #                'GT': self.vldr_params.crosstalk_g_transm,
        #                'GR': self.vldr_params.crosstalk_g_refl,
        #                'sys_err_lower_bound_a': self.vldr_params.depol_uncertainty_params.a_lower,
        #                'sys_err_lower_bound_b': self.vldr_params.depol_uncertainty_params.b_lower,
        #                'sys_err_lower_bound_c': self.vldr_params.depol_uncertainty_params.c_lower,
        #                'sys_err_upper_bound_a': self.vldr_params.depol_uncertainty_params.a_upper,
        #                'sys_err_upper_bound_b': self.vldr_params.depol_uncertainty_params.b_upper,
        #                'sys_err_upper_bound_c': self.vldr_params.depol_uncertainty_params.c_upper,
        #                })
        #
        # # todo: propagate systematic errors through all operations, smoothing etc.
        # self.result.ds = self.calc_routine.run(
        #     sigratio=data.ds,
        #     depol_params=params)
        # self.result.profile_qf = data.profile_qf.copy(deep=True)
        #
        return self.result


registry.register_class(PLDRFactory,
                        PLDRFactoryDefault.__name__,
                        PLDRFactoryDefault)

registry.register_class(CalcPLDR,
                        CalcPLDRDefault.__name__,
                        CalcPLDRDefault)
