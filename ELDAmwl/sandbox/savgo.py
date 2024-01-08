from functools import lru_cache

from PyDynamic.uncertainty.propagate_filter import FIRuncFilter
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from scipy.signal import savgol_coeffs


@lru_cache(maxsize=100)
def sg_coeffs(window_length, order):
    return savgol_coeffs(window_length, order)


window_length = 33

# N = 10
# in_array = np.linspace(-np.pi*N, np.pi*N, 1000)
# out_array = np.sin(in_array)
# data = out_array + np.random.rand(1000) * 0.1
# err = data + np.random.rand(1000) * 0.1

data_before = xr.open_dataset('bsc_before_smooth.nc')
data_after = xr.open_dataset('bsc_after_smooth.nc')

fig = go.Figure()

fig.add_trace(go.Scatter(x=data_before.altitude[0].data, y=data_before.data[0].data))
fig.add_trace(go.Scatter(x=data_after.altitude[0].data, y=data_after.data[0].data))
fig.add_trace(go.Scatter(x=data_before.altitude[0].data, y=data_before.err[0].data))
fig.add_trace(go.Scatter(x=data_after.altitude[0].data, y=data_after.err[0].data))


def ina_sg(data, err):
    sgc = sg_coeffs(window_length, 2)
    err_sm = np.sqrt(np.sum(np.power(err * sgc, 2)))
    data_sm = np.sum(data * sgc)
    return data_sm, err_sm


def sg(data, err):
    sgc = sg_coeffs(window_length, 2)
    data, err = FIRuncFilter(data, err, sgc, kind='diag')
    return data, err


print(data_before.data[0].data[40:70])

a = xr.DataArray(data_before.data[0].data)
a[46:48] = np.NaN
print(a[40:70])
sg_data, sg_err = sg(a.data,data_before.err[0].data)

fig.add_trace(go.Scatter(x=data_after.altitude[0].data[:133-16], y=sg_data[16:133]))
fig.add_trace(go.Scatter(x=data_before.altitude[0].data[:133-16], y=sg_err[16:133]))


fig.show()
