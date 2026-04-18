import xarray as xr
import numpy as np

def read_wrfout(wrfout_file):
    """
    读取WRFOUT文件
    """
    ds = xr.open_dataset(wrfout_file)
    return ds

def read_precipitation(ds,str_precipitation):
    """
    从WRFOUT数据集中读取降水数据
    """
    precip = ds[str_precipitation]  # RAINNC是WRF输出的累计降水变量
    return precip

def extract_wrf_by_latlon_time(ds, var_name, lat_min, lat_max, lon_min, lon_max, start_time, end_time):
    """
    ✅ WRF 专用：根据 经纬度范围 + 时间段 提取变量
    完美适配 wrfout 输出（XLAT, XLONG, Time）
    """
    # 1. 读取变量
    var = ds[var_name]

    # 2. WRF 经纬度裁剪（必须用 XLAT, XLONG ！！！）
    var_cropped = var.where(
        (ds.XLAT >= lat_min) & (ds.XLAT <= lat_max) &
        (ds.XLONG >= lon_min) & (ds.XLONG <= lon_max),
        drop=True
    )
    # 3. WRF 时间裁剪（大写 T 的 Time！！！）
    var_cropped = var_cropped.sel(Time=slice(start_time, end_time))

    return var_cropped

def get_center_point(lat_min, lat_max, lon_min, lon_max):
    # 计算中心点
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    return center_lat, center_lon
