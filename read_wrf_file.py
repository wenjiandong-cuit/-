import xarray as xr
import metpy
from metpy.units import units
def read_yicuo_var(file_path):
    """
    仅读取 WRF 原始变量，不进行网格插值处理
    """
    ds = xr.open_dataset(file_path)
    
    raw_geopot = ds['PH'].values + ds['PHB'].values
    raw_height = raw_geopot / 9.81
    
    # 2. 重新构建 DataArray，手动指定单位
    height_m = xr.DataArray(
        raw_height, 
        coords=ds['PH'].coords, 
        dims=ds['PH'].dims,
        attrs={'units': 'm', 'description': 'Geopotential Height'}
    )
    
    theta_total_K = ds['T'] + 300
    pres_hpa = (ds['P'] + ds['PB']) * 0.01   
    
    height_m = height_m * units.meter
    theta_total_K = theta_total_K * units.K 
    pres_hpa = pres_hpa * units.hPa
    true_temp = metpy.calc.temperature_from_potential_temperature(pres_hpa, theta_total_K)

    return  height_m, theta_total_K, pres_hpa, true_temp
