import xarray as xr
import numpy as np

def calculate_total_precip(rain_series):
    """
    输入时序降水，输出7天累计降水
    """
    return rain_series.isel(Time=-1) - rain_series.isel(Time=0)\
        
def get_center_point(lat_min, lat_max, lon_min, lon_max):
    # 计算中心点
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    return center_lat, center_lon

