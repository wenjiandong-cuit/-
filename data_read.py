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

def extract_wrf_by_latlon_time(ds,var_name, lat_min, lat_max, lon_min, lon_max, start_time, end_time):
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

def calculate_water_vapor_flux(ds):
    """
    计算 WRF 水汽通量 (uqu, vqv) 单位：kg/(m·s)
    需要变量：U, V, QVAPOR, PB, P, PH, PHB
    """
    # 1. 读取基础变量
    U = ds['U']       # 东西风 (m/s)
    V = ds['V']       # 南北风 (m/s)
    QVAPOR = ds['QVAPOR']  # 水汽混合比 (kg/kg)

    # 2. WRF 风场必须从 质量点 → 动量点 插值到同一网格
    u = (U[:, :, :, :-1] + U[:, :, :, 1:]) / 2  # 东西风插值到中点
    v = (V[:, :, :-1, :] + V[:, :, 1:, :]) / 2  # 南北风插值到中点

    # 3. 截取 QVAPOR 匹配风场网格（关键！否则维度不匹配）
    qv = QVAPOR[:, :, :u.shape[2], :u.shape[3]]

    # 4. 计算水汽通量（标准公式）
    g = 9.81
    uqu = (u * qv) / g  # 纬向水汽通量
    vqv = (v * qv) / g  # 经向水汽通量

    return uqu, vqv

def calculate_water_vapor_flux_divergence(ds, uqu, vqv):
    """
    计算 水汽通量散度 (∇·(qu,qv)) 单位：kg/(m²·s)
    输入：uqu, vqv → 来自上面函数
    """
    # 1. 读取 WRF 网格分辨率 dx, dy（米）
    dx = ds['DX'].values
    dy = ds['DY'].values

    # 2. 中央差计算散度（WRF标准算法）
    dudx = (uqu[:, :, :, 1:] - uqu[:, :, :, :-1]) / dx
    dvdy = (vqv[:, :, 1:, :] - vqv[:, :, :-1, :]) / dy

    # 3. 对齐网格，得到最终散度
    div_q = dudx[:, :, :-1, :] + dvdy[:, :, :, :-1]

    return div_q