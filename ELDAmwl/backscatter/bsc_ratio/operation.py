from copy import deepcopy

from addict import Dict

from ELDAmwl.backscatter.bsc_ratio.product import BackscatterRatios
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.utils.constants import RESOLUTION_STR, ANGSTROEM_DEFAULT, MOL_ANGSTROEM_DEFAULT

import numpy as np
import xarray as xr


class StandardBackscatterRatioFactory(BaseOperationFactory):
    """
    """

    name = 'StandardBackscatterRatioFactory'

    def __call__(self, **kwargs):
        assert 'resolution' in kwargs
        res = super(StandardBackscatterRatioFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'StandardBackscatterRatioFactoryDefault' .
        """
        return StandardBackscatterRatioFactoryDefault.__name__


class StandardBackscatterRatioFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`LidarRatios`.
    """

    name = 'StandardBackscatterRatioFactoryDefault'

    resolution = None
    bsc_params = None
    bsc_ratio_profiles = None

    def prepare(self):
        self.resolution = self.kwargs['resolution']
        self.bsc_params = Dict()
        self.bsc_ratio_profiles = Dict()

        all_params = self.params.all_bsc_products(res=self.resolution)
        num_profiles = len(all_params)
        if num_profiles == 0:
            self.logger.warning(f'bsc ratio at 532 cannot be derived because '
                                f'no individual bsc ratio is available with {RESOLUTION_STR[self.resolution]}')
            return num_profiles

        # sort bsc params by wavelength
        for bp in all_params:
            wl = self.target_wl(bp)
            if wl not in self.bsc_params:
                self.bsc_params[wl] = []
            self.bsc_params[wl].append(bp)

        # calculate average if there are more than 1 bsc ratio per wavelength
        for wl in self.bsc_params:
            if len(self.bsc_params[wl]) > 1:
                self.logger.warning(f'there is more than 1 bsc product at wavelength{wl}')
                # self.bsc_ratio_profiles[wl] = self.calc_average(self.bsc_params[wl])
            else:
                prod_id = self.bsc_params[wl][0].prod_id_bsc_ratio_str
                # todo: use qc profiles here (but qc of bsc ratio not yet implemented)
                self.bsc_ratio_profiles[wl] = self.data_storage.basic_product_common_smooth(prod_id,
                                                                                 self.resolution)
        return num_profiles

    def target_wl(self, a_bsc_param):
        # find the closest standard wavelength
        result = None

        for wl in [355, 532, 1064]:
            wl_min = wl - 3
            wl_max = wl + 3
            bsc_wl = a_bsc_param.general_params.emission_wavelength
            if (bsc_wl > wl_min) and (bsc_wl < wl_max):
                result = wl

        return result

    # def calc_average(self, param_list):
    #     """calculates the average of several bsc ratio profiles
    #
    #     Args:
    #         param_list: list of product params of the bsc ratios that shall be averaged
    #
    #     Returns:
    #         :obj:`BackscatterRatios`: the averaged backscatter ratio profile
    #
    #     """
    #     profiles = []
    #     for param in param_list:
    #         prod_id = param.prod_id_bsc_ratio_str
    #         profile = self.data_storage.basic_product_common_smooth(prod_id, self.resolution)
    #         profiles.append(profile.ds.data)
    #
    #     # concatenate all DataArrays along a new dimension
    #     list_array = xr.concat(profiles, 'prod_idx')
    #     mean = list_array.mean(dim='prod_idx')
    #
    #     result = BackscatterRatios()
    #     result.ds['data'] = mean
    #     result.emission_wavelength = profile.emission_wavelength
    #     result.profile_qf = deepcopy(profile.profile_qf)  # todo: average of all profiles
    #
    #     # todo: handle errors, flags, cloud mask and attributes
    #     return result

    def interpolate(self):
        """interpolates the bsc ratios at 355 nm and 1064 nm to 532 nm

        Returns:
            :obj:`BackscatterRatios`: the interpolated backscatter ratio profile at 532nm
        """
        profile_355 = self.bsc_ratio_profiles[355]
        profile_1064 = self.bsc_ratio_profiles[1064]

        profile_532_data = profile_355.ds.data + \
                           (profile_1064.ds.data - profile_355.ds.data) / (1064 - 355) * (532 - 355)

        # result = deepcopy(self.bsc_ratio_profiles[355])
        result = BackscatterRatios.from_signal(profile_355, profile_355.params)
        result.ds['data'] = profile_532_data
        result.ds['qf'] = profile_355.ds.qf | profile_1064.ds.qf
        result.emission_wavelength.values = 532
        result.profile_qf = profile_355.profile_qf | profile_1064.profile_qf

        # todo: testing, handle errors and attributes
        return result

    def extrapolate(self, from_wl):
        """ extrapolates the backscatter ratio at from_wl to 532nm

        Args:
            from_wl: wavelength of source of the extrapolation

        Returns:
            :obj:`BackscatterRatios`: the extrapolated backscatter ratio profile at 532nm
        """
        ae_par = ANGSTROEM_DEFAULT
        ae_mol = MOL_ANGSTROEM_DEFAULT
        source = self.bsc_ratio_profiles[from_wl]

        factor_m = np.power((from_wl / 532), ae_mol)
        factor_p = np.power((from_wl / 532), ae_par)
        factor = factor_p / factor_m

        # create a new, empty instance
        result = BackscatterRatios.from_signal(source, source.params)
        # calculate data
        result.ds['data'] = source.data * factor + (1 - factor)
        result.ds['qf'] = deepcopy(source.ds.qf)
        # set the correct value for emission wavelength
        result.emission_wavelength.values = 532
        result.profile_qf[:] = deepcopy(source.profile_qf[:])

        # todo: testing, handle errors and attributes
        return result

    def get_product(self):
        num_profiles = self.prepare()

        if num_profiles == 0:
            return None

        if 532 in self.bsc_params:
            bsc_ratio = self.bsc_ratio_profiles[532]
        elif (355 in self.bsc_params) and (1064 in self.bsc_params):
            bsc_ratio = self.interpolate()
        elif 355 in self.bsc_params:
            bsc_ratio = self.extrapolate(355)
        elif 1064 in self.bsc_params:
            bsc_ratio = self.extrapolate(1064)
        else:
            self.logger.error(f'no bsc ratio can be derived with {RESOLUTION_STR[self.resolution]}')
            bsc_ratio = None

        return bsc_ratio


registry.register_class(StandardBackscatterRatioFactory,
                        StandardBackscatterRatioFactoryDefault.__name__,
                        StandardBackscatterRatioFactoryDefault)
