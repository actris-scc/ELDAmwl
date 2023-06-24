import xarray as xr
import numpy as np

general = xr.open_dataset('data/ELDAmwl_files/hpb_012_0000598_201810172100_201810172300_20181017oh00_ELDAmwl_v0.0.2.nc',
                          group='/')
hr = xr.open_dataset('data/ELDAmwl_files/hpb_012_0000598_201810172100_201810172300_20181017oh00_ELDAmwl_v0.0.2.nc',
                     group='highres_products')
lr = xr.open_dataset('data/ELDAmwl_files/hpb_012_0000598_201810172100_201810172300_20181017oh00_ELDAmwl_v0.0.2.nc',
                     group='lowres_products')

hr1 = hr.assign(negative_systematic_error_particledepolarization=lambda hr: hr.negative_systematic_error_volumedepolarization * np.nan)
hr2 = hr1.assign(positive_systematic_error_particledepolarization=lambda hr1: hr1.positive_systematic_error_volumedepolarization * np.nan)
hr3 = hr2.assign(particledepolarization=lambda hr2: hr2.volumedepolarization * np.nan)
hr4 = hr3.assign(error_particledepolarization=lambda hr3: hr3.error_volumedepolarization * np.nan)
hr5 = hr4.assign(particledepolarization_meta_data=lambda hr4: hr4.volumedepolarization_meta_data)
hr5.data_vars['particledepolarization_meta_data'][1] = '/meta_data/particledepolarization_532'

for var in ['{}depolarization', 'error_{}depolarization', 'negative_systematic_error_{}depolarization',
            'positive_systematic_error_{}depolarization', '{}depolarization_meta_data']:
    source = hr5.data_vars[var.format('volume')]
    target = hr5.data_vars[var.format('particle')]
    target.attrs = source.attrs
    for att, value in target.attrs.items():
        target.attrs[att] = value.replace('volume', 'particle')

lr1 = lr.assign(volumedepolarization=lambda lr: lr.backscatter * np.nan)
lr2 = lr1.assign(particledepolarization=lambda lr: lr.backscatter * np.nan)
lr3 = lr2.assign(error_volumedepolarization=lambda lr: lr.backscatter * np.nan)
lr4 = lr3.assign(error_particledepolarization=lambda lr: lr.backscatter * np.nan)
lr5 = lr4.assign(negative_systematic_error_volumedepolarization=lambda lr: lr.backscatter * np.nan)
lr6 = lr5.assign(positive_systematic_error_volumedepolarization=lambda lr: lr.backscatter * np.nan)
lr7 = lr6.assign(positive_systematic_error_particledepolarization=lambda lr: lr.backscatter * np.nan)
lr8 = lr7.assign(negative_systematic_error_particledepolarization=lambda lr: lr.backscatter * np.nan)
lr9 = lr8.assign(volumedepolarization_meta_data=lambda lr: lr.backscatter_meta_data)
lr10 = lr9.assign(particledepolarization_meta_data=lambda lr: lr.backscatter_meta_data)
lr10.particledepolarization_meta_data[1] = '/meta_data/particledepolarization_532'
lr10.volumedepolarization_meta_data[1] = '/meta_data/volumedepolarization_532'

for var in ['{}depolarization', 'error_{}depolarization', 'negative_systematic_error_{}depolarization',
            'positive_systematic_error_{}depolarization', '{}depolarization_meta_data']:
    for type in ['volume', 'particle']:
        varname = var.format(type)
        lr10.data_vars[varname].attrs = hr5.data_vars[varname].attrs

ae = xr.DataArray(np.ones((4,2,1027)) * np.nan,
                  dims=['np', 'time', 'level'],
                  coords=dict(level=lr.level, altitude=lr.altitude,  time=lr.time, np=[0,1,2,3]))
ae.name = 'angstroem_exponent'
ae.attrs={'long_name': "angstroem exponent",
          'units': "1",
          'ancillary_variables': "error_angstroem_exponent "
                                 "angstroem_exponent_wavelength_bounds "
                                 "angstroem_exponent_type",
          'coordinates': "altitude"}
ae_wl = xr.DataArray(np.ones((4,2)),
                     dims=['np', 'nv'],
                     coords=dict(np=[0,1,2,3], nv=[0,1]),
                     attrs=dict(long_name="wavelength bounds of the angstroem exponent",
                                units="nm"))
ae_wl.name = "angstroem_exponent_wavelength_bounds"
ae_wl[0] = [355.,532.]
ae_wl[1] = [355.,532.]
ae_wl[2] = [532., 1064.]
ae_wl[3] = [355., 1064.]

ae_type = xr.DataArray(np.array(np.ones(4), dtype=np.byte),
                     dims=['np'],
                     coords=dict(np=[0,1,2,3]),
                     attrs=dict(long_name="type of the products from which the angstroem exponent is derived",
                                units="1", flag_masks=(1,2), flag_meanings="extinction backscatter"))
ae_type.name = 'angstroem_exponent_type'
ae_type[:] = [0,1,1,1]

lr11 = lr10.assign(angstroem_exponent=ae)
lr12 = lr11.assign(angstroem_exponent_wavelength_bounds=ae_wl)
lr13 = lr12.assign(angstroem_exponent_type=ae_type)

general.to_netcdf(path='data/ELDAmwl_files/test.nc', mode='w', group='/', format='NETCDF4')
hr5.to_netcdf(path='data/ELDAmwl_files/test.nc', mode='a', group='highres_products', format='NETCDF4')
lr13.to_netcdf(path='data/ELDAmwl_files/test.nc', mode='a', group='lowres_products', format='NETCDF4')
