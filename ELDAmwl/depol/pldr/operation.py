import numpy as np
from addict import Dict

from ELDAmwl.backscatter.bsc_ratio.product import BackscatterRatios
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
# from ELDAmwl.component.interface import IPLDROp
from ELDAmwl.component.registry import registry
from ELDAmwl.depol.pldr.product import PLDRs
from ELDAmwl.depol.pldr.tools.operation import CalcPLDRProfile
from ELDAmwl.utils.constants import MC, CALC_WINDOW_OUTSIDE_PROFILE, P_ALL_OK

import zope

class PLDRFactory(BaseOperationFactory):
    r"""creates a factory for the retrieval of PLDR profiles.

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

        Returns: always "PLDRFactoryDefault"

        """
        return PLDRFactoryDefault.__name__


class PLDRFactoryDefault(BaseOperation):
    r""" a factory class that derives a single instance of `.PLDRs` .

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

        # vldr and bsc are deepcopies from the data storage
        self.vldr = self.data_storage.basic_product_qc(self.param.vldr_prod_id, self.resolution)
        self.bsc = self.data_storage.basic_product_qc(self.param.bsc_prod_id, self.resolution)

        self.empty_pldr = PLDRs.init(
            self.vldr, self.param, self.resolution)

    def get_non_merge_product(self):

        # create Dict with all params which are needed for the calculation
        pldr_params = Dict({
            'error_method': self.param.error_method,
            'min_bsc_ratio': self.param.min_BscRatio,
        })

        pldr_retrieval_routine = CalcPLDR()(
            pldr_params=pldr_params,
            calc_routine=CalcPLDRProfile()(prod_id=self.prod_id),
            vldr=self.vldr,
            bsc=self.bsc,
            empty_pldr=self.empty_pldr,)
        pldr = pldr_retrieval_routine.run()

        # if self.param.error_method == MC:
        #     adapter = zope.component.getAdapter(pldr_retrieval_routine, IMonteCarlo)
        #     pldr.err[:] = adapter(self.param.mc_params)
        # else:
        #     pldr = pldr
        #
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
    r"""
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


# @zope.interface.implementer(IPLDROp)
class CalcPLDRDefault(BaseOperation):
    r"""Calculates PLDRs from the volume linear depolarization and particle backscatter.

    The result is a copy of empty_pldr, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        pldr_params (`.PLDRParams`): retrieval parameter of the PLDR product
        calc_routine (`.BaseOperation`): result of `.CalcPLDRProfile`
        vldr (`.VLDRs`): volume depolarization ratio
        bsc (`.Backscaters`): particle backscatter coefficient
        empty_pldr (`.PLDRs`): \
                instance of PLDRs which has all meta data but profile data are empty arrays

    Returns:
        `.PLDRs`: profiles of particle linear depolarization ratios

    """

    name = 'CalcPLDRDefault'

    calc_param = None
    calc_routine = None
    vldr = None
    # rayl_depol = None
    bsc = None
    bsc_ratio = None
    result = None
    resolution = None

    def __init__(self, **kwargs):
        super(CalcPLDRDefault, self).__init__(**kwargs)
        self.calc_param = kwargs['pldr_params']
        self.calc_routine = self.kwargs['calc_routine']
        self.vldr = self.kwargs['vldr']
        # self.rayl_depol = self.vldr.ds['molecular_depolarization_ratio'].copy(deep=True)
        self.bsc = self.kwargs['bsc']
        self.bsc_ratio = self.data_storage.basic_product_common_smooth(self.bsc.params.prod_id_bsc_ratio_str,
                                                                      self.vldr.resolution)
        self.result = self.kwargs['empty_pldr'].copy()


    def run(self, vldr=None, bsc=None):
        """         run the pldr calculation

        The the optional keyword args 'vldr' and 'bsc' allow to feed new input data into
        an existing instance of CalcPLDRDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals.
        If no keeword parameters are provided, the calculation runs with the data that were provided for init()

        Keyword Args:
            vldr (:class:`ELDAmwl.depol.vldr.product.VLDRs`): VLDR profiles, default=None
            bsc (:class:`ELDAmwl.backscatter.common.product.Backscatters`): particle backscatter profiles, default=None

        Returns:
            profiles of PLDR (:class:`ELDAmwl.lidar_ratio.product.PLDRs`)

        """
        if vldr is None:
            vldr = self.vldr
        if bsc is None:
            bsc = self.bsc
            bsc_ratio = self.bsc_ratio
        else:
            bsc_ratio = BackscatterRatios.from_bsc(bsc)

        params = Dict({'calc_stat_err': ~ (self.calc_param.error_method == MC),
                       })

        # calculate PLDR data
        self.result.ds = self.calc_routine.run(
            vldr=vldr.ds,
            bsc_ratio=bsc_ratio.ds,
            calc_params=params,
            )

        if vldr.has_sys_err:
            # calculate systematic errors
            vldr_max = vldr.copy()
            vldr_max.ds['data'] = vldr.data + vldr.ds.sys_err_pos
            pldr_max = self.calc_routine.run(
                vldr=vldr_max.ds,
                bsc_ratio=bsc_ratio.ds,
                calc_params=params,
                )
            vldr_min = vldr.copy()
            vldr_min.ds['data'] = vldr.data - vldr.ds.sys_err_neg
            pldr_min = self.calc_routine.run(
                vldr=vldr_min.ds,
                bsc_ratio=bsc_ratio.ds,
                calc_params=params,
                )
            self.result.ds['sys_err_pos'] = pldr_max.data - self.result.data
            self.result.ds['sys_err_neg'] = self.result.data - pldr_min.data

            del vldr_max
            del vldr_min
            del pldr_max
            del pldr_min

        # todo: propagate systematic errors through all operations, smoothing etc.
        self.result.resolution = vldr.resolution
        self.result.profile_qf = vldr.profile_qf | bsc.profile_qf
        self.result.ds['qf'] = vldr.qf | bsc.qf

        for t in np.where(self.result.profile_qf == P_ALL_OK)[0]:
            lvb = min(vldr.last_valid_bin(t), bsc.last_valid_bin(t))
            fvb = max(vldr.first_valid_bin(t), bsc.first_valid_bin(t))
            self.result.ds.qf[t, lvb:] = self.result.ds.qf[t, lvb:] | CALC_WINDOW_OUTSIDE_PROFILE
            self.result.ds.qf[t, :fvb] = self.result.ds.qf[t, :fvb] | CALC_WINDOW_OUTSIDE_PROFILE

        return self.result


registry.register_class(PLDRFactory,
                        PLDRFactoryDefault.__name__,
                        PLDRFactoryDefault)

registry.register_class(CalcPLDR,
                        CalcPLDRDefault.__name__,
                        CalcPLDRDefault)
